# File Research: sources/os/plan9/9front/sys/src/9/omap/lexception.s

ARM exception vector and trap-entry assembly.

Key behavior:
- Defines the vector stubs and vector table copied to high vectors by `trapinit`.
- `_vsvc` handles SWI/system-call entry, saves user registers into `Ureg`, calls `syscall`, restores state, and returns with `RFE`.
- Undefined, prefetch-abort, data-abort, IRQ, and FIQ vector paths switch to SVC mode and call `trap`.
- Handles separate save/restore paths for traps originating in kernel versus user mode.
- `setr13` installs per-mode stack pointers for IRQ/FIQ/abort/undefined/system modes.

Research notes:
- The file carefully avoids ambiguous writeback forms of MOVM/LDM/STM, with comments referencing known assembler/architecture pitfalls.
- FIQ currently returns without dedicated handling.
