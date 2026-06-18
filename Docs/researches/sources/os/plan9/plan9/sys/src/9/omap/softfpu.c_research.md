# File Research: sources/os/plan9/plan9/sys/src/9/omap/softfpu.c

Soft-FPU placeholder and ARM floating-point instruction emulation hook.

Key responsibilities:
- Provides machine-dependent FPU lifecycle stubs expected by port code: `/proc` FPU I/O, notify/noted, rfork save/copy, process save/restore, exec setup, and init.
- Implements `fpuemu(Ureg*)`, which lowers priority, calls `fpiarm(ureg)` to emulate an ARM floating-point instruction, restores priority, and posts a debug note on error.

Important behavior:
- All FPU state-management routines are no-ops except `fpuemu`.
- `fpudevprocio` returns 0 and does not expose register state.

Dependencies:
- Depends on the soft-float emulator function `fpiarm`.
- Called by trap/syscall paths through machine-dependent hooks.

Notable risks:
- No real FPU context is saved/restored; this platform relies on software emulation or absence of hardware FPU use.
