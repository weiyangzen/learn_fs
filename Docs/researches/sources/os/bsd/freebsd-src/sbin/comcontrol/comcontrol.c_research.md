# File Research: sources/os/bsd/freebsd-src/sbin/comcontrol/comcontrol.c

## Purpose
Gets or sets tty drain-wait behavior on a file descriptor or device.

## Main Elements
- `usage()`: documents `comcontrol <filename> [drainwait <n>]`.
- `main()`: opens the target or uses stdin for `-`, reads `TIOCGDRAINWAIT` when no setting is supplied, and writes `TIOCSDRAINWAIT` for `drainwait`.

## Dependencies And Integration
Uses tty ioctls from system headers. It is a small wrapper around kernel tty control.

## Risk Notes
The setter validates only the first character of the numeric argument with `isdigit()` and then uses `atoi()`, so partial numeric strings are accepted.
