# File Research: sources/os/bsd/openbsd-src/sys/sys/pipe.h

Defines kernel pipe buffer and per-pipe state structures.

Key contents:
- Pipe buffer sizes `PIPE_SIZE` and `BIG_PIPE_SIZE`.
- `struct pipebuf`: count, in/out indices, size, and KVA buffer pointer.
- Pipe state bits for async I/O, reader/writer wait, rundown, EOF, exclusive lock, and lock wait.
- `struct pipe`: lock pointer, buffer, kqueue list, timestamps, async I/O registration, peer link, pair storage, state, and busy count.
- Locking annotations for immutable, sigio-lock, and pipe-lock fields.

Kernel API:
- `pipe_init()`.

Risk notes:
- Pipe state combines buffer-ring accounting, kqueue notification, SIGIO registration, and bidirectional peer linkage.
