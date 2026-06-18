# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfileio.c

## Purpose
Implements PostScript file I/O operators: reads, writes, line and string operations, flushing, seeking, filename lookup, proc-filter checks, and stdin/stdout/stderr callouts.

## Key Functions
- `zclosefile()`, `zread()`, `zwrite()`, `zwritestring()`, `zprint()`, `zflush()`, and `zflushfile()` implement basic I/O.
- `zreadhexstring_at()`, `zwritehexstring_at()`, `zreadstring_at()`, and `zreadline_at()` perform partial I/O with continuation support.
- `zbytesavailable()`, `zfileposition()`, `zxfileposition()`, and `zsetfileposition()` expose stream availability and seek state.
- `zfilename()`, `zisprocfilter()`, `zpeekstring()`, `zunread()`, and `zwritecvp()` implement Ghostscript extensions.
- `handle_read_status()` and `handle_write_status()` translate `INTC`/`CALLC` stream statuses into continuations.

## Important Behavior
- Partial reads/writes store an index or residual substring and resume through internal continuation operators.
- Stream error strings are copied into `$error.errorinfo` once.
- `readstring` intentionally returns `rangecheck` for zero-length strings to match Adobe behavior.
- `.peekstring` does not consume buffered bytes.

## Research Notes
Tightly coupled to `zfproc.c` because procedure streams use `CALLC` continuations.
