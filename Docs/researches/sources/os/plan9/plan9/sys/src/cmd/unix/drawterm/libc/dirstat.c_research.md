# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirstat.c

This file returns allocated `Dir` data for a path.

Key behavior:
- `dirstat` calls `stat`, decodes with `convM2D`, and returns allocated `Dir` plus string storage.

Important details:
- Mirrors `dirfstat` for pathname input.
