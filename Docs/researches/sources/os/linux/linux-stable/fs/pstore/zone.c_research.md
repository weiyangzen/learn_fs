# File Research: sources/os/linux/linux-stable/fs/pstore/zone.c

## Summary
Implements the pstore/zone intermediate backend used by pstore/blk. It partitions a linear storage backend into in-memory zones, recovers persisted zone contents, writes dmesg/pmsg/console/ftrace records, tracks dirty zones, and registers an embedded pstore backend.

## Main Responsibilities
- Define generic zone headers and dmesg subheaders.
- Allocate zones for pmsg, console, ftrace, and dmesg according to `pstore_zone_info`.
- Recover existing records from storage after reboot.
- Write dmesg records into rotating kmsg zones and circular frontend records into their zones.
- Flush dirty zones synchronously or through delayed work.
- Erase records from storage or mark metadata cleared.
- Export `register_pstore_zone()` and `unregister_pstore_zone()`.

## Key Interfaces
- `register_pstore_zone()` validates backend geometry/callbacks, allocates zones, builds `struct pstore_info`, and calls `pstore_register()`.
- `unregister_pstore_zone()` unregisters pstore, flushes dirty zones, frees memory, and resets counters.
- `psz_pstore_read()`, `psz_pstore_write()`, and `psz_pstore_erase()` implement backend operations.
- `psz_recovery()` performs first-use recovery from storage.
- `psz_zone_write()` updates memory and optionally flushes metadata, data, or full zones.

## Important Behavior
The storage area is laid out as pmsg, console, ftrace, then dmesg zones. Each zone has a `psz_buffer` header with signature, data length, start offset, and data. Dmesg zones additionally store `psz_kmsg_header` with magic, timestamp, compression flag, counter, and dump reason.

Recovery treats dmesg specially: it first reads only headers to validate zones, find newest crash sequence, set the next write slot, and recover oops/panic counters; then it reads full data only for valid zones. Console, pmsg, and ftrace use circular old buffers.

Writes prefer not to damage old records before recovery. If storage writes cannot be completed, zones are marked dirty and a delayed cleaner retries. Panic dmesg writes set `on_panic`, suppress non-dmesg writes, and flush all dirty zones when possible.

For kmsg writes, broken zones signaled by `-ENOMSG` cause the writer to try subsequent dmesg zones. The write path temporarily swaps in a fresh buffer so an old in-memory buffer can be restored if the attempted zone fails.

## State and Synchronization
A singleton `psz_context` holds all zones, counters, recovery state, panic state, backend info, and embedded pstore backend. `pstore_zone_info_lock` serializes registration/unregistration. Dirty flags and recovery/panic state are atomic.

## Cross-File Interactions
`blk.c` registers pstore/blk devices through this layer. `platform.c` consumes the embedded `struct pstore_info`. `ftrace.c` supplies log-combining logic for ftrace zone reads.

## Risks
Correctness depends on zone sizes being sector-aligned and large enough for headers. Dirty-zone retry behavior can leave data only in memory until backend writes succeed. Panic writes depend on backend `panic_write` availability for reliable crash persistence.
