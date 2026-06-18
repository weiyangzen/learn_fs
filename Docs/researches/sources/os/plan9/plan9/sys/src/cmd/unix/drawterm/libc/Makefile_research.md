# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/Makefile

This Makefile builds drawterm's bundled `libc.a`.

Key contents:
- Includes `../Make.config`.
- Archives Plan 9 libc compatibility objects for formatting, 9P packing, directory helpers, UTF/rune handling, networking helpers, random/time, TLS/SSL push helpers, and encoders.
- Uses `$(CC) $(CFLAGS)` and standard archive commands.

Important details:
- Some source files in the directory are not in `OFILES` and therefore are optional/unused for this build.
