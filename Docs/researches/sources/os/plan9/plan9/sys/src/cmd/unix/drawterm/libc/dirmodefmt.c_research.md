# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirmodefmt.c

This file formats Plan 9 directory mode bits.

Key behavior:
- `dirmodefmt` renders type and permission bits as a textual mode string.
- `rwx` fills read/write/execute triples.

Important details:
- Handles Plan 9 mode flags such as directory, append, exclusive, auth, temporary, and device-specific bits.
