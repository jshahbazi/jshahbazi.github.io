---
layout: post
category: Apps
tags: [local AI, LLM, Apple silicon, inference engine, Rust, Metal, open source]
description: "Stark is a free, open-source Mac app that downloads and runs open-weight language models on Apple silicon. A guided setup picks a model for your Mac with no Terminal involved and connects it to OpenWork or OpenCode Desktop in one click, and the same engine exposes an OpenAI-style local API, native worker processes and a candidate-scoring path for people who want to build on it. On a matched checkpoint it decoded 9.2% faster than MLX-Serve."
title: "Introducing Stark, a Local AI Engine for Apple Silicon"
---

[Stark](https://starkengine.app/) is a free, open-source Mac app that downloads an open-weight language model, runs it on your Mac's GPU, and makes it available to chat with or to other apps on the same machine. It also installs and connects the apps most people will actually do their work in: [OpenWork](https://openworklabs.com/) for everyday tasks on files and OpenCode Desktop for coding, with no API key to copy. I built it for two kinds of people at once: someone who has never opened Terminal and wants to run a model locally, and an engineer who wants to drive the engine from code and cares about tokens per second. This post explains how I tried to serve both without making either side worse off.

<!--more-->

Most of my earlier posts are about evaluating small models and decision models such as JevK5 in a training pipeline. Doing that work meant running a lot of local inference on Macs, and the tools I used for it were either comfortable for engineers and opaque to everyone else, or friendly to beginners and slow or limited for engineers. Stark is the engine I ended up building for myself, packaged so that other people can use it.

Stark is a menu bar app for Apple silicon Macs (M1 or newer, macOS 26.4 or newer) with two interfaces, Beginner and Advanced, that share the same installed models. Beginner checks your memory, GPU budget and storage, recommends a model, downloads it, starts it and opens a chat, with no Terminal involved. It then walks you through installing OpenWork or OpenCode Desktop and connects them to the running model in one click. Advanced exposes the model catalog, imports from source checkpoints, and generation settings. Under both is a Rust and Metal engine, forked from [Uzu](https://github.com/trymirai/uzu) and heavily modified, that serves an OpenAI-style HTTP API on `127.0.0.1:8000`, exposes native generation and scoring workers over stdin/stdout, and (depending on the model) converts Safetensors and MLX checkpoints into its own format. On a same-checkpoint comparison with Qwen3.8-Flash-Next on an M5 Max, Stark's maximum observed decode rate was 66.81 tokens per second against 61.17 for MLX-Serve, a 9.2% difference. On Qwen3.5-2B across six workloads it led MLX-LM, vLLM Metal, llama.cpp and TensorFold, with 12.2% higher aggregate throughput than MLX-LM.

In this post I'll go through the two audiences and why I did not want to pick one, cover how Stark gets a model into OpenWork or OpenCode, walk through what the Beginner path does and how it chooses a model, cover what the engine exposes for engineers, give the performance numbers and their limits, and then say what is next.

## Two audiences, one engine

The people who want to run a model locally fall into two groups with very different needs. The first group has heard that you can run AI on your own machine, likes the privacy of it, and wants to type a question and get an answer. For this group the barriers are all up front: which model, which quantization, will it fit in memory, what is a GGUF, why is Terminal involved at all. Most of them never get past those questions.

The second group already knows the answers. They want to pick the exact checkpoint, see the tokens per second, point a coding tool at a local endpoint, and sometimes bypass the HTTP layer entirely and talk to the engine from their own process. For this group the barriers are the opposite: tools that hide settings, lock the model choice, or sit on a slow runtime.

Most existing tools serve one of these groups well and tolerate the other. I did not want to ship two apps, because the second group also benefits from a setup flow that gets a model running in three clicks, and the first group eventually grows into wanting the catalog. So Stark has one engine, one set of installed models, and two interfaces. Switching between Beginner and Advanced is a menu item.

## Getting a model into OpenWork or OpenCode

A running model by itself is a chat window. Most people want it to read a document, draft a reply, summarize a folder of notes, or edit code, and that takes a separate app that can see files and call tools. Stark does not try to be that app. It runs the model and connects two apps that already do this well: OpenWork for everyday work on files, and OpenCode Desktop for coding. Both are installed separately, and Stark can open the download page or the installed app for you.

The connection is three steps from the menu bar.

1. Install OpenWork (choose macOS, Apple silicon) and open a local workspace, which is the folder it is allowed to work in. Start with a folder containing one test file.
2. In Stark, click the cat, then Connections, then Apps. With a model running in Chat mode, click Connect on the OpenWork row. Stark writes the connection into OpenWork; there is no API key to copy and no base URL to type.
3. If Stark asks, quit OpenWork and reopen it. In OpenWork's model picker choose Stark and the running model, and keep Stark open while you work.

The same flow applies to OpenCode Desktop. For any other OpenAI-compatible client, Connections has a Connect your own app option that shows the Base URL, API key and Model ID to paste in.

## What the Beginner path does

The Beginner path is a guided setup with five steps. A good amount of the design effort went here.

- **It checks the Mac first.** Before recommending anything, Guided setup reads unified memory, estimates the GPU budget, and checks free storage. The recommendation depends on the result.
- **It asks what you want to do, not which model you want.** The first question is writing, files or coding. The model recommendation follows from that and from the hardware check. A model name is shown, but the user does not have to know what it means to proceed.
- **It reuses what is already installed.** If a suitable model is already on disk, the guide offers to use it rather than downloading again.
- **It ends in a chat.** After the model starts, the guide prompts a short conversation so the user sees the model working before being asked to connect anything else.
- **It continues into OpenWork or OpenCode.** For regular work or coding, the guide's remaining steps install the app, choose a workspace folder, and make the connection described above.

## What the engine exposes for engineers

The Advanced interface is the catalog, source imports and generation settings. The parts engineers will care about more are underneath it.

- **A local HTTP API.** Default base `http://127.0.0.1:8000/v1`, with `GET /v1/models`, `GET /v1/capabilities` and `POST /v1/chat/completions` supporting JSON and SSE streaming. Omitting `model` targets whichever model is running. Bearer authentication uses a persistent key stored in macOS Keychain. The listener is loopback only and rejects browser-origin requests. Any OpenAI-compatible client works by pasting the Base URL, key and model ID; OpenWork and OpenCode Desktop connect with one click.
- **Native worker processes.** `stark generate` and `stark score` are standalone processes that accept one JSON request per line on stdin and reply on stdout. The host owns chat-template rendering, tool execution and the agent loop; the worker owns the model. This is the path for anyone who does not want an HTTP server in the middle.
- **Candidate token scoring.** `stark score` returns next-token logits for 2 to 16 candidate token IDs, with full-vocabulary log probabilities and temperature-scaled candidate probabilities. The caller owns the decision rule. This is what I use for JevK5 and the app's Decision mode, and it is the reason the engine exists in its current form.
- **A converter.** `stark convert` takes a Hugging Face checkpoint or a local folder with complete Safetensors weights, config, tokenizer and chat template, and produces a native artifact. Existing MLX 4-bit and 8-bit exports are repacked without requantizing. Qwen3.8-Flash-Next, GLM-5.3-Flash and Recursive Flint run on native paths for prepared quantized checkpoints.
- **Prefix reuse.** Connected apps resend the whole conversation each turn. On supported text paths Stark reuses the unchanged beginning of the previous request. On a synthetic Qwen3-4B 4-bit test with 19,000 to 21,000-token prompts, follow-up prompt processing went from 7.6 to 8.6 seconds without reuse to 0.6 to 1.4 seconds with it. Those are prompt-processing times, not full response times.
- **Terminal tools.** An install script puts the CLI under `~/.local` and the app under `~/Applications` without sudo, and checks the archive checksum before activating anything. `stark doctor` checks the install; `stark chat --model-path` runs a model in Terminal.

The supported model list covers Qwen3, Qwen3.5 and Qwen2 dense models, Llama 3.1 and 3.2, Mistral 7B, Codestral and Devstral, Gemma 2 and Gemma 3 text, Phi-4-mini, Granite, SmolLM2 and SmolLM3, LFM2 and Llamba, plus the native paths for Qwen3.8-Flash-Next, GLM-5.3-Flash and Flint. Image input is supported for Qwen3.5 dense BF16 checkpoints only, one PNG or JPEG per request. Embeddings, the Responses API and JSON-schema structured output are not supported. Family support means the code path exists; each checkpoint still needs compatible metadata and a successful native load.

## Performance

Stark is fast. On Qwen3.5-2B, it beat every other engine I could put on the same Mac: 245.5 tokens per second aggregate across six end-to-end workloads, ahead of MLX-LM at 218.8, vLLM Metal at 174.7, llama.cpp at 147.9 and TensorFold at 125.6. Not a cherry-picked workload; Stark led all six. On Qwen3.8-Flash-Next with identical checkpoint files, it decoded 9.2% faster than MLX-Serve, and with multi-token prediction switched on it peaked at 82.85 tokens per second on an M5 Max.

Every number comes from a recorded run with the method, build hashes and raw records published. The [technical page](https://starkengine.app/technical.html#benchmarks) has all three studies and their limits.

## What's next

The immediate work is adding reviewed tool-calling templates for more models.  And more models themselves.  And image support for models

But more importantly, user feedback is what will guide future development.
