# File Research: sources/os/bsd/dragonflybsd/sys/sys/sockbuf.h

This header defines a generic mbuf-chain socket buffer structure and low-level buffer manipulation macros/functions.

Key responsibilities:
- Defines kernel `struct sockbuf`:
  - actual byte count
  - mbuf memory count
  - preallocation byte/memory counts
  - I/O data limit
  - mbuf chain head
  - last mbuf
  - last record
- Defines default `SB_MAX`.
- Defines debug `sbcheck()` behavior.
- Defines counter macros:
  - `sballoc()`
  - `sbprealloc()`
  - `sbfree()`
- Defines inline `sbinit()`.
- Declares append, append-address, append-control, append-record, append-stream, compress, create-control, drop, drop-record, unlink, check, and flush functions.

Important invariants:
- `sballoc()` and `sbfree()` account both mbuf header size and external storage size.
- Preallocation counters are updated atomically.
- `sb_lastrecord` is valid only when `sb_mb` is non-NULL.
- `sbinit()` clears all counters and chain pointers while setting the caller-provided limit.

Research notes:
- `sockbuf.h` is lower-level than `socketvar.h`; `signalsockbuf` embeds it and adds locking/notification state.
