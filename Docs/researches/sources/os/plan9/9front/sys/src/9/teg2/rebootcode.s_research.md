# File Research: sources/os/plan9/9front/sys/src/9/teg2/rebootcode.s

ARMv7 low-memory reboot trampoline.

Purpose:
- Runs from `REBOOTADDR` after `main.c` copies it there.
- Disables caches/MMU and copies a new kernel image to its physical destination before jumping to the new entry point.

Key behavior:
- `main` prints reboot progress, calls `cachesoff`, warps to physical execution, copies kernel code with `memmove`, and branches to the physical entry address.
- `cachesoff` drains and disables L1 cache/MMU/control bits with barriers.
- Includes local `_r15warp`, `panic` stub, `pczeroseg` stub, and `printhex`.

Integration:
- The C `reboot()` function prepares arguments and cache state, then jumps here.

Risks/notes:
- Must fit below page-table-sensitive low-memory limits.
- Assumes PL310/L2 is already off before entry.
