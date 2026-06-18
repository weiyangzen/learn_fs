# File Research: sources/os/plan9/9front/sys/src/9/port/log.c

Generic circular action log used by devices/subsystems that expose readable debug/event logs.

Key responsibilities:
- Lazily allocates a circular buffer on first open and frees it on last close.
- Serializes readers with `readq`.
- Blocks reads until at least `minread` bytes or requested bytes are available.
- Supports `set` and `clear` log control messages against named `Logflag` masks.
- Appends raw buffers with `logn()` and formatted strings with `log()`.
- Drops oldest data when the circular buffer would overflow.

Important behavior:
- Logging is skipped unless the mask is enabled and the log has open readers.
- Oversized single log records larger than the buffer are dropped.
- Readers receive wrapped data through two `memmove()` operations when needed.

Notable risks:
- `logctl()` silently ignores unknown flag names but rejects malformed verbs.
