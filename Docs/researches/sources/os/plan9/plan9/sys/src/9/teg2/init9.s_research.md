# File Research: sources/os/plan9/plan9/sys/src/9/teg2/init9.s

Small assembly entry wrapper for the first user-space boot program.

Key behavior:
- Sets Plan 9 static base register `R12`.
- Passes `/boot/boot` style argument pointers to `startboot`.
- Calls `startboot(SB)` and then loops forever if it returns.

Notes:
- Kept in assembly because setting `SB` in C would pull in too much runtime code.
- Matches the conceptual C shape `main(argv0) { startboot(argv0, &argv0); }`.
