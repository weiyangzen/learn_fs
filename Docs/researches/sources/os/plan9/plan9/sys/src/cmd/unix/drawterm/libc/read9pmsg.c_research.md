# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/read9pmsg.c

This file reads one complete 9P message from an fd.

Key behavior:
- `read9pmsg` reads the 4-byte size prefix, validates it against the caller buffer, then reads the rest with `readn`.

Important details:
- Returns the full message size or `0`/`-1` for EOF/error.
