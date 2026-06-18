# File Research: sources/os/plan9/plan9/sys/src/cmd/pump.c

Purpose: Copies input to output through a shared circular buffer, separating reading and writing into different processes.

Key behavior:
- Options configure read/write block sizes, sleep delay, output file, buffer size in KB, initial prefill, seek offset, and output byte/time-style limit.
- Allocates circular buffer, forks with shared memory using `rfork(RFMEM)`.
- Child reads one or more files/stdin into buffer with backpressure.
- Parent writes from buffer to stdout or output file.
- Uses `Lock` to protect `nin`, `nout`, `done`, and buffer counters.
- Supports prefill before publishing `nin`.

Dependencies and integration:
- Plan 9-specific `rfork`, shared memory, `Lock`, and libc.

Risks and notes:
- `done` is shared memory state; process lifetime and exit ordering matter.
- `verb` is never set by options.
- `tsize` option multiplies minutes by a magic byte count, suggesting a throughput/time approximation.
- Error paths may stop one side while the other notices via `done` or EOF.
