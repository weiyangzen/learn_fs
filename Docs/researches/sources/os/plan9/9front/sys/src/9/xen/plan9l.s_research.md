# File Research: sources/os/plan9/9front/sys/src/9/xen/plan9l.s

Plan 9 user-entry and syscall-vector assembly for Xen x86.

Purpose:
- Provides `touser` and direct syscall vector handling.

Key behavior:
- `touser` builds an x86 interrupt-return frame with user selectors, user stack, IF set, and entry `UTZERO+32`, loads user data segments, then `IRETL`s.
- `_syscallintr` saves segment and general registers, switches DS/ES to kernel data selector, calls `syscall(Ureg*)`, restores registers/segments, drops trap metadata, and returns with `IRETL`.

Integration:
- Used by `init0()` in `main.c` and by `trapinit` vector table from `l.s`.

Risks/notes:
- Assumes syscall vector `0x40` and exact `Ureg`/trap-frame stack layout.
