# File Research: sources/os/bsd/freebsd-src/sys/kern/tty_compat.c

## Purpose
Maps historical BSD tty ioctls and sgtty-style flags to modern `termios` operations when `COMPAT_43TTY` support routes unknown tty ioctls here.

## Main Structures and State
- `struct speedtab` maps integer baud rates to old compact speed codes.
- `compatspeeds[]` and `compatspcodes[]` translate between old speed indices and numeric rates.
- `ttydebug` sysctl under `debug.ttydebug` enables trace prints.

## Core Behavior
- `tty_ioctl_compat()` handles old setters (`TIOCSETP`, `TIOCSETN`, `TIOCSETC`, `TIOCSLTC`, `TIOCLBIS`, `TIOCLBIC`, `TIOCLSET`) by copying current termios, translating legacy state with `ttsetcompat()`, and re-entering `tty_ioctl()`.
- It handles old getters (`TIOCGETP`, `TIOCGETC`, `TIOCGLTC`, `TIOCLGET`) by projecting current termios into legacy structures.
- Old line discipline commands and console command aliases are mapped to modern `TIOCSETD`/`TIOCCONS` behavior.
- `ttcompatgetflags()` reconstructs old `sg_flags`/local flags from modern input/output/control/local flags.
- `ttcompatsetflags()` and `ttcompatsetlflags()` apply old RAW/CBREAK/CRMOD/PASS8/LITOUT/parity/echo/local flag semantics into termios.

## Dependencies
Uses `struct tty`, `struct termios`, compatibility ioctl structure definitions, and the generic `tty_ioctl()` path.

## Notes and Risks
- This is a translation layer, not a separate line discipline.
- It preserves legacy quirks such as rounded-down speed mapping and approximate RAW/CBREAK detection.
