# File Research: sources/os/plan9/plan9/sys/src/9/teg2/lexception.s

ARM exception vector and trap-entry assembly.

Key behavior:
- Defines vector stubs and vector table entries for reset, undefined instruction, SWI, aborts, hypervisor, IRQ, and FIQ.
- `_vrst` starts additional CPUs through `cpureset`.
- `_vsvc` builds a `Ureg` for system calls, restores kernel `SB`, sets `m`/`up`, calls `syscall`, then returns to user mode.
- `_vswitch` handles undefined, abort, and IRQ paths by switching to SVC mode, building `Ureg`, and calling `trap`.
- Separates user-origin and kernel/SVC-origin trap frames.
- `rfue` and `forkret` paths return through ARMv7 `RFE`.

Notes:
- Carefully avoids ambiguous `MOVM.W` behavior by separating store-multiple and stack adjustment.
- FIQ and hypervisor entries only print diagnostics and return.
