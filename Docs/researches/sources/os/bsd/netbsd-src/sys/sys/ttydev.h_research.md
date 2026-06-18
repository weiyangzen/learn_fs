# File Research: sources/os/bsd/netbsd-src/sys/sys/ttydev.h

Read completely: 60 lines.

Compatibility header for old tty speed codes.

Key elements:
- If `USE_OLD_TTY` is defined, maps old compact speed code numbers for `B0` through `B115200` plus `EXTA`/`EXTB`.
- Otherwise defines no active API beyond the include guard.

Risks and notes:
- Compatibility-only; modern `termios.h` speed constants use actual baud values.
- Code compiled with `USE_OLD_TTY` sees different numeric speed values.
