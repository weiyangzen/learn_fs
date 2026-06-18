# File Research: sources/os/plan9/plan9/sys/src/9/port/syscallfmt.c

Formats syscall entry and return traces.

Entry formatting:
- `syscallfmt` builds a string in `up->syscalltrace` containing pid, process text, syscall name/number, PC, and decoded arguments.
- Handles strings, argv arrays, fd/path/stat buffers, read/write buffers, offsets, segment operations, mount/bind arguments, semaphores, rendezvous, and time calls.
- `fmtuserstring` validates and copies a user NUL-terminated string.
- `fmtrwdata` validates and formats up to a bounded data buffer as printable ASCII with non-printables replaced by `.`.

Return formatting:
- `sysretfmt` formats return values, output buffers for read/errstr/await/fd2path, error string, and start/stop timestamps.
- For failed calls, it uses `up->syserrstr`.

Important behavior:
- Frees any previous `up->syscalltrace` before replacing it.
- Uses `validaddr`, `validalign`, and `vmemchr`, so tracing itself touches user memory and can raise kernel errors if invalid.
- Write data and read data are capped at 64 bytes in trace output.

Role:
- Debug/tracing support for Plan 9 syscalls.
