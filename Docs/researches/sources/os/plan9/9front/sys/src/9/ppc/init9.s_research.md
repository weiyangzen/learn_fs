# File Research: sources/os/plan9/9front/sys/src/9/ppc/init9.s

Tiny PowerPC user-mode trampoline for the first process init code.

Key responsibilities:
- Defines `_main` that sets the static base register, creates a small stack frame, passes `argv0` and `&argv0` to `startboot()`, then loops forever if `startboot()` returns.

Dependencies:
- Used with `port/initcode.c`/`initcode.i` rather than full libc startup to keep init code small.
