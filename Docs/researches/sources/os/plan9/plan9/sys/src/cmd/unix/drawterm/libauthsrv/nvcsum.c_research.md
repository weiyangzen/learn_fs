# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/nvcsum.c

This file implements the Plan 9 NVRAM checksum.

Key behavior:
- `nvcsum` rotates and adds bytes to produce an 8-bit checksum.

Important details:
- Used by `readnvram.c` to validate stored auth secrets.
