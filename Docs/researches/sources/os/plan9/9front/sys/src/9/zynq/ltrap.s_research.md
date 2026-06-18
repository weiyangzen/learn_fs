# File Research: sources/os/plan9/9front/sys/src/9/zynq/ltrap.s

Purpose: Zynq ARM exception vector and trap/syscall entry assembly.

Key behavior:
- `vectors` branches reset/undefined/SVC/prefetch abort/data abort/IRQ/FIQ slots to handlers.
- Exception paths save SPSR/CPSR/LR and general registers into a `Ureg` frame, reload Mach/up from TPIDRPRW, and call `trap`.
- SVC path builds syscall frame and calls `syscall`.
- Return paths restore SPSR/registers and return to user or interrupted mode.

Integration notes: Uses `mem.h` processor-mode constants and Plan 9 `trap`/`syscall` C handlers.

Risk/attention points: Correct frame shape is critical for `trap`, `syscall`, and `userureg` interpretation.
