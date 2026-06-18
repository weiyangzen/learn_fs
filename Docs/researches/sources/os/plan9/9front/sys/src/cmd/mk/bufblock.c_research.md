# File Research: sources/os/plan9/9front/sys/src/cmd/mk/bufblock.c

Provides reusable growable buffers for parser, shell, and formatting code.

Key behavior:
- `newbuf()` allocates or reuses a `Bufblock` with a 4096-byte quantum.
- `freebuf()` puts buffers on a freelist.
- `growbuf()` either swaps backing storage with a suitably large free buffer or reallocates the current buffer.
- Provides byte/rune/string insertion and copy helpers.

Important dependencies: `mk.h`, `Malloc`, `Realloc`, Plan 9 Rune conversion.

Notable risks:
- `freebuf()` does not free memory; buffers persist for reuse.
- Callers must insert NUL terminators explicitly when needed.
