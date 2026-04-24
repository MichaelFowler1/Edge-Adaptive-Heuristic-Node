# Edge-Adaptive Heuristic Node

A local Python agent that uses offline LLM inference to iteratively optimize and rewrite its own source code. Designed to run completely air-gapped, it uses hardware telemetry to measure performance changes and dynamically hot-swaps its code while running.

## Proof of Execution
The log below shows the agent successfully proposing a structural update, bypassing a Linux file lock using an atomic swap, and restarting its main loop with the newly generated code.

![Hot-Swap Execution Log](image_883d4c.png)

## Architecture

This project is built around the idea of treating source code as a mutable state during runtime. 

* **Hardware Telemetry:** Instead of relying on arbitrary software counters, the agent queries the local GPU (tested natively on an NVIDIA RTX 3080) for utilization and temperature. This allows it to measure the actual computational footprint of its logic updates.
* **Air-Gapped Operation:** Powered locally by the `qwen2.5-coder:14b` model via Ollama. It makes no external API calls, ensuring complete data privacy and offline capability.
* **AST Syntax Guarding:** Before applying any generated code, the agent parses the proposed changes through Python's `ast` module. This acts as a safeguard to catch syntax errors and prevent the agent from accidentally breaking its own runtime loop.
* **Atomic Hot-Swapping:** To bypass kernel-level file read-locks during execution, the agent uses `os.replace` to write to a temporary file and atomically swap it with the active script. It then uses `os.execv` to restart the process seamlessly.

Because this engine interacts with system-level file states, it is recommended to run it within an isolated virtual environment.
