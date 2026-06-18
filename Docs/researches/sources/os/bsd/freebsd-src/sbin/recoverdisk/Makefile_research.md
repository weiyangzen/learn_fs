# File Research: sources/os/bsd/freebsd-src/sbin/recoverdisk/Makefile

Build file for `recoverdisk`.

Key elements:
- Builds `recoverdisk` in package `runtime`.
- Adds `-lm` for math functions.
- Provides a simple local `test` target running `./recoverdisk /dev/ad0`.

Dependencies:
- Uses `bsd.prog.mk`.
