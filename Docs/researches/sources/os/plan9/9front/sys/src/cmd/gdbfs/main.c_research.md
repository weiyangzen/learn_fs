# File Research: sources/os/plan9/9front/sys/src/cmd/gdbfs/main.c

## Purpose
Presents a GDB remote target as a Plan 9 `/proc`-style 9P filesystem.

## Key Elements
Builds files `ctl`, `fpregs`, `kregs`, `mem`, `regs`, `text`, and `status` under a process-named directory; supports reading memory/registers/text/status, writing memory/control, flushing blocking control requests, stat sizing for registers/text, command parsing for `stop`, `start`, `waitstop`, and `startstop`, and optional TCP dialing to a remote address.

## Dependencies
Uses Plan 9 lib9p, thread server APIs, libmach text or architecture selection, and the GDB protocol layer in `gdb.c`.

## Behavior/Risks
Requires either `-t text` or `-m arch`. `fpregs` and register writes are not implemented. Mounts before `/proc`, so it intentionally overlays process-like entries for debugger clients.
