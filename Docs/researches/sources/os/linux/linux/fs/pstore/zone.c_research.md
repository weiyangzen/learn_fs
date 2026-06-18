# File Research: sources/os/linux/linux/fs/pstore/zone.c

## Role

Implements the reusable pstore/zone intermediate backend used by pstore/blk-style storage. It manages in-memory zones, flushes them to a contiguous backing store, recovers old records after reboot, and registers a pstore backend.

## Data Model

- `struct psz_buffer`: per-zone on-storage header with signature, data length, circular start offset, and data.
- `struct psz_kmsg_header`: dmesg-specific subheader with magic, timestamp, compression bit, counter, and reason.
- `struct pstore_zone`: one in-memory zone with storage offset, type/name, current buffer, recovered old buffer, size, recovery flag, and dirty flag.
- `struct psz_context`: global singleton with kmsg/pmsg/console/ftrace zones, counters, recovery/panic flags, backend info lock, and embedded `pstore_info`.

## Writes and Flushes

- `psz_zone_write()` updates in-memory data and optionally flushes none/part/meta/all to backend `write` or `panic_write`.
- Dirty zones are marked when writes cannot be flushed, and a delayed cleaner retries later.
- `psz_flush_all_dirty_zones()` retries pmsg, console, kmsg, and ftrace zones.
- Panic state blocks non-dmesg writes and attempts to flush other dirty zones after panic dmesg writes.

## Recovery

- `psz_recovery()` runs once before reads.
- Kmsg recovery first scans metadata to validate headers, find latest write position, and recover oops/panic counters, then reads full data for valid zones.
- Pmsg, console, and ftrace recovery load old circular data into `oldbuf`.
- Recovery avoids damaging old records before storage is known readable.

## Record Operations

- `psz_pstore_open()` resets read counters.
- `psz_pstore_write()` dispatches records by type.
- `psz_pstore_read()` recovers if needed, then returns kmsg, combined ftrace, pmsg, and console records.
- `psz_pstore_erase()` clears kmsg zones by count match or frees old buffers for other record types.
- Ftrace reads combine per-CPU zone logs using `pstore_ftrace_combine_log()`.

## Registration

- `register_pstore_zone()` validates sizes, alignment, total capacity, name, and read/write callbacks; allocates zones; creates pstore dmesg buffer; sets flags; and registers with core pstore.
- `unregister_pstore_zone()` unregisters pstore, flushes dirty zones, frees buffers/zones, clears counters, and resets recovery/panic state.

## Research Notes

This layer turns arbitrary sector-like storage into pstore frontends while preserving crash-path behavior. The implementation is singleton-based, assumes one backend at a time, and treats `panic_write` as the only safe panic-time storage path.
