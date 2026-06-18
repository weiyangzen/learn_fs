# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/bufblock.c

Provides reusable growable byte buffers for `mk`.

Key functions:
- `newbuf()` returns a buffer from freelist or allocates a new `QUANTA`-sized buffer.
- `freebuf()` puts a buffer on the freelist.
- `growbuf()` grows current capacity, optionally swapping with a larger freelist buffer.
- `bufcpy()` appends raw bytes.
- `insert()` appends one byte.
- `rinsert()` appends one UTF rune.

Behavior notes:
- `growbuf()` preserves existing contents and adjusts `current`.
- Buffers are not freed back to the OS during normal operation; they are pooled.
