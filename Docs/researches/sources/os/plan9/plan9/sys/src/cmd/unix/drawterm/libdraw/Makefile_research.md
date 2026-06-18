# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/Makefile

This Makefile builds drawterm's `libdraw.a`.

Key contents:
- Includes `../Make.config`.
- Archives a small draw support library: allocation, arithmetic, bytes-per-line, channel parsing, default font, replication drawing, trig helpers, rectangle clipping, and RGB helpers.
- Uses `$(CC) $(CFLAGS)` and archive commands.

Important details:
- The listed sources are not part of this work item, but the Makefile establishes the draw library boundary used by drawterm GUI/kernel code.
