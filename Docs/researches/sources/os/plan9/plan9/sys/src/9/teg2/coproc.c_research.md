# File Research: sources/os/plan9/plan9/sys/src/9/teg2/coproc.c

Runtime-generated ARM coprocessor access helpers for CP15 and VFP control/register operations.

Key responsibilities:
- Builds tiny instruction buffers containing `MRC`/`MCR`, `VMRS`/`VMSR`, `VSTR`, or `VLDR`, followed by a return instruction.
- Flushes data and instruction caches so generated instruction buffers are executable.
- Provides generic `cprd`/`cpwr` and CP15-specific `cprdsc`/`cpwrsc`.
- Provides VFP control access (`fprd`, `fpwr`) and double-precision register save/restore (`fpsavereg`, `fprestreg`).

Important behavior:
- Operations run with interrupts disabled to keep the generated instruction sequence stable.
- FP reads/saves panic if the CPU's FPU state is marked off, while `fpwr` is allowed because it may enable the FPU.

Dependencies and assumptions:
- Depends on executable stack/local instruction buffers, `cachedwbse`, `cacheiinv`, `coherence`, and ARM instruction encodings.
- Assumes return via `MOV R14, R15` is suitable for these generated snippets.

Notable risks:
- Dynamic instruction generation is sensitive to cache coherency and instruction encoding correctness.
- This approach exists because ARM hard-wires coprocessor register numbers into instructions.
