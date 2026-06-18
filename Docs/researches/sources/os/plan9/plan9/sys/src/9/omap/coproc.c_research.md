# File Research: sources/os/plan9/plan9/sys/src/9/omap/coproc.c

Provides runtime-generated ARM coprocessor and VFP register access helpers.

Key points:
- Dynamically builds small instruction sequences on the stack for `MCR`, `MRC`, `VMRS`, and `VMSR`, followed by a return instruction.
- `MAP2PCSPACE()` maps generated instruction memory into the caller PC’s segment so it can execute correctly under current mappings.
- Flushes written instruction sequences with `cachedwbse()` and invalidates I-cache before execution.
- `cpwr()` writes arbitrary coprocessor register fields; `cpwrsc()` specializes it to CP15/system control.
- `cprd()` reads arbitrary coprocessor register fields; `cprdsc()` specializes it to CP15.
- `fprd()` and `fpwr()` read/write VFP system registers.

Dependencies and interactions:
- Used by `archomap.c`, `clock.c`, cache/MMU code, and FP setup.
- Requires cache maintenance and coherence helpers from assembly.

Research relevance:
- A compact dynamic-instruction mechanism that avoids hand-writing every CP15/VFP accessor.
