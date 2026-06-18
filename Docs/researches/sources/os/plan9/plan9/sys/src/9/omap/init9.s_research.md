# File Research: sources/os/plan9/plan9/sys/src/9/omap/init9.s

Provides the tiny assembly entry for Plan 9 user boot initialization.

Key points:
- Equivalent to a C `main(char *argv0) { startboot(argv0, &argv0); }`.
- Written in assembly to set static base (`SB`) without pulling in extra C runtime routines.
- Loads `R12` with `setR12(SB)`.
- Passes `boot(SB)` and a pointer to the frame argument area to `startboot(SB)`.
- Loops forever after `startboot()` returns.

Dependencies and interactions:
- Used as initial user/bootstrap code in the OMAP Plan 9 environment.
- Depends on `startboot` and `boot` symbols from the boot/user setup.

Research relevance:
- Minimal startup shim ensuring the Plan 9 boot process enters `startboot()` with SB correctly established.
