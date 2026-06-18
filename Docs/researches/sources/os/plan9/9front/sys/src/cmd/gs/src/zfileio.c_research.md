# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfileio.c

## Purpose
Implements PostScript file I/O operators: reads, writes, line and string operations, flushing, seeking, filename lookup, proc-filter checks, and stdin/stdout/stderr callouts.

## Key Functions
- `zclosefile()`, `zread()`, `zwrite()`, `zwritestring()`, `zprint()`, `zflush()`, and `zflushfile()` implement basic I/O.
- `zreadhexstring_at()` / `zreadhexstring_continue()` parse hexadecimal input with continuation state.
- `zwritehexstring_at()` / `zwritehexstring_continue()` write hex text in chunks.
- `zreadstring_at()` / `zreadstring_continue()` read string data, preserving partial progress across callouts.
- `zreadline_at()` / `zreadline_continue()` read lines while handling CR/LF interruption edge cases.
- `zreadline_from()` dispatches to `gp_readline` for stdin and `sreadline` otherwise.
- `zbytesavailable()`, `zfileposition()`, `zxfileposition()`, and `zsetfileposition()` expose stream availability and seek state.
- `zfilename()`, `zisprocfilter()`, `zpeekstring()`, `zunread()`, and `zwritecvp()` implement Ghostscript extensions.
- `zneedstdin()`, `zneedstdout()`, and `zneedstderr()` return interpreter callout errors.
- `file_switch_to_read()` and `file_switch_to_write()` switch read/write files between modes.
- `handle_read_status()` and `handle_write_status()` translate stream `INTC`/`CALLC` statuses into e-stack continuations.

## Important Behavior
- Several operators reserve stack space before reading so retry after stack overflow cannot lose consumed bytes.
- Partial reads/writes store an index or residual substring and resume through internal continuation operators.
- Stream error strings are copied into `$error.errorinfo` once by `copy_error_string()`.
- `readstring` intentionally returns `rangecheck` for zero-length strings to match Adobe behavior.
- `.peekstring` does not consume buffered bytes and refuses requests larger than the current stream buffer.

## Research Notes
This file is tightly coupled to `zfproc.c` because procedure streams use `CALLC` continuations for external read/write callbacks.
