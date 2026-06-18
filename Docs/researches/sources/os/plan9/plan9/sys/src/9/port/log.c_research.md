# File Research: sources/os/plan9/plan9/sys/src/9/port/log.c

Purpose: Shared in-kernel circular log buffer implementation for devices such as `devsdp`.

Key logic:
- `logopen` allocates a default 4 KiB ring buffer and initializes pointers on first open.
- `logclose` frees the buffer on final close.
- `logread` blocks until at least `minread` bytes are available, then copies from the circular buffer with wrap handling.
- `logctl` accepts `set`/`clear` followed by named flags and updates `logmask`.
- `logn` appends raw bytes if the mask is enabled and log is open, dropping oldest bytes on overflow.
- `log` formats into a stack buffer then calls `logn`.

Dependencies and integration:
- Uses `Log` and `Logflag` structures from kernel headers, `Rendez`, `QLock`, and `Lock`.

Risks and notes:
- Logs are not retained when no file is open.
- Messages larger than the log buffer are silently dropped by `logn`.
