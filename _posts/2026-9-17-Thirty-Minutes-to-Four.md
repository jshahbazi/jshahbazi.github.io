---
layout: post
title: "Thirty Minutes to Four"
category: Infrastructure
tags: [Docker, Cloud Build, GitHub Actions, Claude Code]
description: "Our GPU training image took thirty minutes to build on every merge, docs-only merges included. Claude Code traced 24 of those minutes to one chown and one missing cache flag. Code-only builds now finish in about four."
---

<style>
.entry table {
  margin: 2rem 0;
  font-family: var(--mono);
  font-size: 0.82rem;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.entry table th {
  text-align: right;
  font-weight: 500;
  color: var(--muted);
  border-bottom: 1px solid var(--border-strong);
  padding: 0.35rem 0.9rem;
  font-size: 0.74rem;
  letter-spacing: 0.04em;
}
.entry table th:first-child,
.entry table td:first-child { text-align: left; white-space: normal; }
.entry table td {
  text-align: right;
  padding: 0.5rem 0.9rem;
  border-bottom: 1px solid var(--border);
  color: var(--text-soft);
}
.entry table tbody tr:last-child td { border-bottom: 1px solid var(--border-strong); }
.entry table strong { color: var(--accent); font-weight: 600; }
.entry .caption {
  font-family: var(--sans);
  font-size: 0.78rem;
  color: var(--muted);
  margin-top: -1.4rem;
  margin-bottom: 2rem;
}
</style>

Every merge to main that touches shared code rebuilds our GPU training image: torch, vLLM, deepspeed, and the CUDA compatibility libraries that let a CUDA 13 build run on the drivers Vertex AI requires. The build runs on Cloud Build because no GitHub-hosted runner has the disk for it, and it took thirty minutes. Every single time. And one morning I even had three of them running at once, and two of the three were only documentation merges (my fault for letting a README.md change trigger the action).

So I asked Claude Code why it took so long.

TL;DR: Always ask your advanced AI models *why*

<!--more-->

## Finding out where the time went

It read the workflow first, which turned out to be a thin shim: authenticate, submit a Cloud Build config, wait. So the question moved to Cloud Build. It pulled the phase timings for the most recent build, then pulled the build log out of Cloud Logging and lined up the timestamp on every Dockerfile step. Then it fetched the image manifest from Artifact Registry and mapped each layer's compressed size back to the instruction that produced it.

| Phase | Time |
|---|---|
| GitHub Actions setup | 0.5 min |
| Cloud Build queue | 0.8 min |
| `uv sync` (245 packages) | 2.2 min |
| vLLM probe, CUDA debs, gcc | 1.0 min |
| `useradd` + `chown -R` | **9.2 min** |
| Push to Artifact Registry (12.4 GB) | **15.3 min** |
| Resolve digest, propose pin | 0.3 min |

Two lines account for 24 of the 29 minutes.

## A chown that cost eight gigabytes

The Dockerfile ended the way a lot of Dockerfiles end: create a non-root user, `chown -R` the virtualenv to it, switch users. Reasonable. Except overlay2 implements a chown by copying every touched file up into a new layer, and the venv held four gigabytes of compressed wheels.

It was worse than a copy. uv's wheel cache lived inside the image (`UV_CACHE_DIR=/tmp/uv-cache`), and uv hardlinks the venv to that cache. The chown touched both trees, the copy-up broke the hardlinks, and the new layer held two full copies. The `uv sync` layer was 4.0 GB compressed. The chown layer on top of it was 8.0 GB. The image we pushed was 12.4 GB for about 4.4 GB of payload.

Claude Code inferred this from the sizes. It never listed the layer's contents, and it said so. 8,026 MB sitting on top of 4,020 MB is hard to explain any other way, but I appreciated the distinction.

The push took fifteen minutes because it was pushing that layer. Docker pushes layers in parallel, and the 8 GB one finished last.

## No layer was ever reused

The second problem was quieter. Every source directory was copied before `uv sync`, so any code change invalidated the dependency install and the 4 GB layer got rebuilt and re-pushed. The Cloud Build config had no `--cache-from`, so even an unchanged lockfile started from nothing on a fresh worker. In the push log, only the five base-image layers ever said `Layer already exists`.

And `README.md` was in the workflow's `paths:` filter, because the Dockerfile copied it for setuptools' package metadata. Every docs PR touches the README. So every docs merge rebuilt and pushed 12 GB.

## The fixes

Claude Code ranked three fixes by payoff. I asked it to implement all three and to double-check its own work.

1. **Create the user first and let uv install as that user.** Same venv ownership as before, with no rewrite. `UV_NO_CACHE=1` keeps the wheel cache out of the image entirely.
2. **Install dependencies before copying source.** `uv sync --no-install-project` from `pyproject.toml` and `uv.lock` alone, then copy the source and run a second `uv sync` for the editable install. Cloud Build pulls the previous `:latest` and builds with `--cache-from` against it.
3. **Stop copying the README.** setuptools only needs the file to exist. The Dockerfile writes a stub, and README.md came out of the path filter.

The Dockerfile's shape, before and after:

```dockerfile
# Before
COPY pyproject.toml uv.lock README.md ./
COPY apps/training ./apps/training
COPY packages ./packages
RUN uv sync --frozen --no-dev --group training
# ... CUDA compat libs, nvcc, gcc ...
RUN groupadd --system app && useradd --system --gid app app \
 && chown -R app:app /app/.venv /tmp/uv-cache
USER app
```

```dockerfile
# After
ENV UV_NO_CACHE=1
RUN groupadd --system app && useradd --system --gid app app \
 && mkdir -p /app && chown app:app /app
COPY --chown=app:app pyproject.toml uv.lock ./
USER app
RUN printf '# stub\n' > README.md \
 && uv sync --frozen --no-dev --group training --no-install-project
USER root
# ... CUDA compat libs, nvcc, gcc ...
COPY apps/training ./apps/training
COPY packages ./packages
USER app
RUN uv sync --frozen --no-dev --group training
```

Everything a code change can invalidate now sits below the CUDA layers, so those stay cached too.

## Results

It verified with two live builds on the branch. The first was cold: the previous `:latest` still had the old layout, so nothing could hit the cache. The second was warm.

| Build | Cloud Build | Image | Layers uploaded |
|---|---|---|---|
| Before | 28 min | 12.41 GB | 11 |
| Cold (new Dockerfile) | 18.6 min | 4.37 GB | 11 |
| Warm | **2 min 20 s** | 4.37 GB | **0** |

The cold build spent five minutes pulling the old 12 GB image one last time, built in five and a half with the chown gone, and pushed the new 4 GB dependency layer in eight. The warm build hit the cache on all nineteen Dockerfile steps, uploaded nothing, and produced a byte-identical digest. Its entire cost was two minutes pulling the 4.4 GB cache image. End to end, the GitHub Actions run went from thirty minutes to a little over four.

The warm build was also a better test than I had planned. A teammate's docs pass landed on the branch while the cold build was running, so the commit it built changed the README and some comments and nothing else. That is exactly the case that used to cost thirty minutes.

## Double-checking

"Double check your work" turned out to be worth saying. It re-read the final Dockerfile, ran the contract tests it had added (layer order, no recursive chown, no shipped cache, the cache warm-up step), and trial-merged both branches onto main. Then it went back to the registry and streamed the tar headers of the pushed layers to confirm the venv and the editable install were owned by the runtime user and the source trees were still root-owned, which is what the old chown had produced.

It also caught two of its own mistakes on the way. It had read the tar link-count column as the uid and streamed the wrong layer on the first pass. And a comment a teammate had reworded was accurate for one branch but would become false the moment the companion branch merged. It fixed both and said which.

## Takeaways

- **Map layer sizes to instructions before touching anything.** The registry manifest plus the image config's history gives you a bill of materials per Dockerfile line. The build log never showed the 8 GB layer. That table put it on the first row.
- **`chown -R` is a copy.** On overlay2 it rewrites every file it touches into a new layer. Create the user first and install as that user, or leave a root-owned, world-readable venv alone.
- **A layer cache is a contract about instruction order.** Dependencies keyed on the lockfile, source after. Without `--cache-from` on a fresh worker, none of it matters.
- **Path filters are code.** README.md sat in `paths:` because a Dockerfile copied it. Nobody wrote that down as a decision, and it cost thirty minutes per docs merge.
- **Ask for verification.** The fix was ordinary Docker lore. The loop paid for itself: dispatch, watch, read the log, inspect the layers, find the stale comment.

## Final thoughts

Every one of these fixes is in some Docker best-practices document, and I have written variants of that chown line myself. The diagnosis is what I want to remember: four systems (GitHub Actions, Cloud Build, Cloud Logging, Artifact Registry), one sitting, and one thread of reasoning that went from "this action is slow" to "this specific line produced this specific eight-gigabyte layer" with the evidence attached. I would not have sat down to do that between other things. The model did it well.
