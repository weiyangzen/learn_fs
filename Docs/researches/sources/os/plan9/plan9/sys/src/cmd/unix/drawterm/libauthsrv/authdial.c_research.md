# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/authdial.c

This file locates and dials a Plan 9 auth server.

Key behavior:
- `authdial` looks up auth server information with NDB helpers and dials the selected service.

Important details:
- Uses network database and Biobuf interfaces.
- Present source is not included in `libauthsrv/Makefile`.
