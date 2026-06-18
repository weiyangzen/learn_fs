# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodevsc.c

## Purpose
Alternative implementation of `%stdin%`, `%stdout%`, and `%stderr%` IODevices using procedure-backed streams and callouts.

## Key Functions
- `stdio_close()` closes and invalidates standard stream IDs.
- `stdin_open()`, `stdout_open()`, and `stderr_open()` create proc streams tagged by integer procedure refs.
- `zget_stdin()`, `zget_stdout()`, and `zget_stderr()` retrieve or create the streams.
- `zis_stdin()` recognizes the special stdin proc stream.

## Important Behavior
- Literal integer refs identify standard streams: `0` stdin, `1` stdout, `2` stderr.
- Allocates buffers manually when the proc stream has none.
- Stdin proc stream sets `min_left` to zero.
- Closing increments IDs to block stale file object access.

## Research Notes
Designed for environments where stdio is mediated through interpreter callouts.
