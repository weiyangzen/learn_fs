# File Research: sources/os/plan9/9front/sys/src/cmd/pump.c

Buffered copy tool using a shared-memory circular buffer between an input process and output process. It can write to stdout or a file, tune buffer/read/write sizes, prefill before output, sleep between output polls, and stop after a time-derived byte limit.

Key behavior:
- Allocates `kilo` KB ring buffer.
- `rfork(RFPROC|RFNOWAIT|RFNAMEG|RFMEM)` creates a shared-memory child for input.
- `doinput` reads files/stdin into the ring while respecting free space.
- `dooutput` writes available data while respecting output block size and optional limit.
- `arithlock` protects 64-bit counters `nin`/`nout`.

Integration points:
- Plan 9-specific `rfork`, `Lock`, and shared memory semantics.

Risks:
- Parent sets `done = 1` after `dooutput`, but with shared-memory concurrency, lifecycle ordering is subtle.
- The `-t` option multiplies by a hard-coded `10584000` “minutes” constant; semantics are not obvious.
- No condition variables; sleeps poll for progress.
