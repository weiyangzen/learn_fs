# File Research: sources/os/bsd/openbsd-src/sbin/dump/Makefile

## Purpose
Builds `dump` and hard-links/installs it as `rdump`.

## Key Contents
- Sources: `itime.c`, `main.c`, `optr.c`, `dumprmt.c`, `tape.c`, `traverse.c`.
- Defines `RDUMP`.
- Links with `libutil`.
- Documents debugging knobs `DEBUG` and `TDEBUG`.

## Notes
The comments accurately describe each module’s role in the dump pipeline.
