# File Research: sources/os/plan9/9front/sys/src/9/teg2/lexception.s

ARM exception-vector entry code for Tegra 2.

Purpose:
- Defines `vectors` and `vtable`, which `trapinit()` copies to low and high vector pages.
- Handles reset, SWI/syscall, undefined instruction, prefetch abort, data abort, IRQ, FIQ, and hypervisor-call vector entries.

Key behavior:
- `_vsvc` saves user registers into a `Ureg`, restores kernel `SB`, recovers `m`/`up`, calls `syscall`, then returns through `rfue`.
- `_vswitch` normalizes abort/IRQ/undefined entries into SVC-mode `trap(Ureg*)` calls for both user and kernel exceptions.
- `setr13` installs banked stack/save-area pointers for ARM exception modes.

Integration:
- Pairs directly with `trap.c` trap decoding and `lproc.s` user return.
- Uses `machaddr`, `MACH`, `USER`, and Plan 9 ARM calling conventions.

Risks/notes:
- Stack layout is exact and shared with `Ureg` consumers.
- FIQ and hypervisor-call vectors are mostly diagnostic stubs that print markers and return.
