---
layout: post
category: Apps
tags: [local AI, LLM, Apple silicon, inference engine, Rust, Metal, open source]
description: "Stark is a free, open-source Mac app that runs AI models on Apple silicon. Guided setup picks a model for your Mac and connects it to OpenWork or OpenCode Desktop in one click; engineers get an OpenAI-style local API, native workers and candidate scoring. It beat MLX-LM, vLLM Metal, llama.cpp and TensorFold on all six Qwen3.5-2B workloads."
title: "Introducing Stark, a Local AI Engine for Apple Silicon"
---

[Stark](https://starkengine.app/) is a free, open-source Mac app that runs AI models on your own machine. Pick a model, it downloads it, runs it on your Mac's GPU, and gets it working inside the apps you'll actually use: [OpenWork](https://openworklabs.com/) for everyday tasks on files, OpenCode Desktop for coding. No Terminal, no API keys, nothing leaves your Mac. I built it for two people at once: someone who has never touched a command line, and an engineer who wants raw tokens per second and a clean API. Stark does both, and this post is about how.

<!--more-->

I've spent the last few months evaluating small models and decision models like JevK5 on Macs, and every local inference tool I tried was made for engineers and baffling to everyone else. Stark is the engine I built for everyone, not just engineers.

It's a menu bar app for Apple silicon Macs (M1 or newer, macOS 26.4 or newer) with both a beginner and advanced interface that share one set of installed models. Beginner mode checks your memory, GPU and storage, picks a model that fits, downloads it, starts it, and drops you into a chat. Then it walks you into OpenWork or OpenCode and connects them in one click. Advanced mode opens up the full model catalog, source imports and generation settings. Underneath both is a Rust and Metal engine, forked from [Uzu](https://github.com/trymirai/uzu) and rebuilt heavily, with an OpenAI-style local API, native generation and scoring workers, and a converter for Safetensors and MLX checkpoints.

It's pretty fast, too. Same checkpoint, same Mac, Stark decodes Qwen3.8-Flash-Next 9.2% faster than MLX-Serve, and on Qwen3.5-2B it beat MLX-LM, vLLM Metal, llama.cpp and TensorFold on every one of six workloads. The part you'll really notice is prefix reuse: when OpenWork or OpenCode sends back a 20,000-token conversation for the next turn, Stark skips the part it has already seen. Follow-ups that took around 8 seconds to start now take around 1. No more waiting while the model rereads the whole chat.

## Made for everyone who wants to use local AI

People who want local AI split into two camps. The first has heard you can run AI on your own machine, likes the privacy, and/or just wants to type a question. Everything stands in their way up front: which model, which quantization, does it fit in memory, what's a GGUF, why is Terminal involved, what is a Terminal. Most never get past that, and who can blame them?  Even the simplest apps out there aren't really geared toward beginners.

The second camp already knows how to handle all of that. They want to pick the exact checkpoint, watch the tokens per second, point a coding tool at a local endpoint, and sometimes skip HTTP and talk to the engine straight from their own process. Their problem is the opposite: tools that hide settings, lock the model, or run slow.

Most tools pick one camp and tolerate the other. I didn't want two apps, because engineers also like a model running in three clicks, and beginners eventually want the catalog. So: one engine, one set of models, two interfaces, and a menu item to switch.

## Getting a model into OpenWork or OpenCode

A model on its own is just like a chat box. What you actually want is for it to read a document, draft a reply, summarize a folder of notes, or edit your code, and that takes an app that can see files and call tools. Stark doesn't try to be that app. It runs the model and plugs it into two apps that already do this well: OpenWork for everyday work on files, OpenCode Desktop for coding. Stark can open the download page or launch the app for you.

Connecting takes three steps from the menu bar.

1. Install OpenWork (macOS, Apple silicon) and open a workspace, the folder it's allowed to work in. Start with a folder holding one test file.
2. In Stark, click the cat, then Connections, then Apps. With a model running in Chat mode, click Connect on the OpenWork row. Stark writes the connection into OpenWork. No API key to copy, no base URL to type.
3. If Stark asks, quit and reopen OpenWork. Pick Stark and the running model in OpenWork's model picker, keep Stark open, and go.

OpenCode Desktop works the same way. Anything else that speaks the OpenAI API gets a Connect your own app option with the Base URL, API key and Model ID ready to paste.

## What Beginner mode does

Beginner mode is a five-step guided setup, and a lot of the design effort went here.

- **It checks your Mac first.** Unified memory, GPU budget, free storage. The recommendation depends on what it finds.
- **It asks what you want to do, not which model you want.** Writing, files or coding. A model name appears, but you don't need to know what it means to keep going.
- **It reuses what you already have.** If a suitable model is on disk, no second download.
- **It ends in a chat.** You see the model working before you're asked to connect anything.
- **It continues into OpenWork or OpenCode.** The remaining steps install the app, choose a folder, and make the connection above.

## What Advanced mode does

Advanced mode is the catalog, source imports and generation settings. The interesting parts are below it.

- **A local HTTP API.** `http://127.0.0.1:8000/v1` with `GET /v1/models`, `GET /v1/capabilities` and `POST /v1/chat/completions`, JSON or SSE streaming. Omit `model` and it targets whatever is running. Bearer auth with a key in macOS Keychain, loopback only, browser-origin requests rejected. Paste the Base URL, key and model ID into any OpenAI-compatible client.
- **Native worker processes.** `stark generate` and `stark score` take one JSON request per line on stdin and answer on stdout. You own the chat template, tool execution and the agent loop; the worker owns the model. No HTTP server in the middle.
- **Candidate token scoring.** `stark score` returns next-token logits for 2 to 16 candidate IDs, with full-vocabulary log probabilities and temperature-scaled candidate probabilities. You own the decision rule. This is what runs JevK5 and the app's Decision mode, and it's why the engine exists.
- **A converter.** `stark convert` takes a Hugging Face checkpoint or a local folder with Safetensors weights, config, tokenizer and chat template, and produces a native artifact. MLX 4-bit and 8-bit exports are repacked without requantizing. Qwen3.8-Flash-Next, GLM-5.3-Flash and Recursive Flint run on native paths.
- **Prefix reuse.** Connected apps resend the whole conversation every turn. Stark reuses the unchanged beginning. On 19,000 to 21,000-token prompts, follow-up prompt processing went from 7.6–8.6 seconds to 0.6–1.4 seconds.
- **Terminal tools.** One install script puts the CLI under `~/.local` and the app under `~/Applications`, no sudo, checksum verified. `stark doctor` checks the install; `stark chat --model-path` runs a model in Terminal.

Supported families: Qwen3, Qwen3.5 and Qwen2 dense, Llama 3.1 and 3.2, Mistral 7B, Codestral and Devstral, Gemma 2 and Gemma 3 text, Phi-4-mini, Granite, SmolLM2 and SmolLM3, LFM2 and Llamba, plus native paths for Qwen3.8-Flash-Next, GLM-5.3-Flash and Flint. Image input works on Qwen3.5 dense BF16 checkpoints, one PNG or JPEG per request. Not yet: embeddings, the Responses API, JSON-schema output.

## Performance

Stark is fast. On Qwen3.5-2B it beat every engine I could put on the same Mac: 245.5 tokens per second across six end-to-end workloads, ahead of MLX-LM at 218.8, vLLM Metal at 174.7, llama.cpp at 147.9 and TensorFold at 125.6. Not one lucky workload; Stark won all six. On Qwen3.8-Flash-Next with identical checkpoint files it decoded 9.2% faster than MLX-Serve, and with multi-token prediction on it hit 82.85 tokens per second on an M5 Max.

Every number is from a recorded run with the method, build hashes and raw records published. The [technical page](https://starkengine.app/technical.html#benchmarks) has all three studies and their limits.

## What's next

More models with reviewed tool-calling templates, more models full stop, and image support beyond Qwen3.5. Past that, the people using it decide. Download it at [starkengine.app](https://starkengine.app/), the source is on [GitHub](https://github.com/jshahbazi/stark) under MIT, and I want to hear what breaks.
