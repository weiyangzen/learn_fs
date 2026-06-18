# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodevs.c

## Purpose
Implements `%stdin%`, `%stdout%`, and `%stderr%` IODevices using direct C stdio/file streams.

## Key Functions
- `stdin_init()` marks stdin as interactive by default.
- `stdin_open()`, `stdout_open()`, and `stderr_open()` create or reopen standard streams.
- `s_stdin_read_process()` fills stdin buffers through `gp_stdin_read()`.
- `zget_stdin()`, `zget_stdout()`, and `zget_stderr()` expose standard streams to other interpreter code.
- `zis_stdin()` identifies stdin streams.

## Important Behavior
- Standard files may be closed and reopened, receiving new stream IDs.
- Stdin has a custom read process that reads one character at a time when interactive.
- Streams and buffers are allocated in system memory.
- IODevice state is temporarily used to carry the current interpreter context during open.

## Research Notes
Direct host-stdio implementation of Ghostscript standard IODevices.
