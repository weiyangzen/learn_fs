# sources/user-network-fs/samba/source3/profile/profile.c

## Purpose

`profile.c` implements Samba smbd profiling collection when profiling support is enabled. It maintains global and per-service counters/timers, receives runtime profiling control messages, dumps per-process statistics into `smbprofile.tdb`, aggregates exited worker data, and exposes collection helpers.

## Important APIs, Types, and Functions

- Globals `profile_p` and `smbprofile_state` hold active profile stats and configuration.
- `set_profile_level()` switches profiling off/counts/full/reset and wipes per-service/profile TDB data on reset.
- `profile_message()` and `reqprofile_message()` handle `MSG_PROFILE` and `MSG_REQ_PROFILELEVEL`.
- `profile_setup()` opens `smbprofile.tdb`, registers message handlers, initializes `profile_p`, and computes the stats magic value.
- `smbprofile_dump_setup()`, `smbprofile_dump_schedule_timer()`, and `smbprofile_dump()` schedule and write profile records.
- `smbprofile_cleanup()` moves a dead worker’s stats into a destination summary record.
- `smbprofile_collect()` aggregates profile records through `profile_read.c`.
- Per-service helpers `smbprofile_persvc_mkref()`, `smbprofile_persvc_unref()`, `smbprofile_persvc_get()`, `smbprofile_persvc_collect()`, and `smbprofile_persvc_reset()` track service-specific activity.

## Control Flow

`profile_setup()` opens `cache_path("smbprofile.tdb")` with mutex locking when writable, optionally registers messaging callbacks, points `profile_p` at the global stats structure, and stores a magic value derived from profile layout. Runtime messages call `set_profile_level()` to adjust counters/timers or reset values.

`smbprofile_dump()` runs when scheduled or called. It exits quickly when profiling is inactive or DB is missing, chain-locks the PID key, parses any previous record, accumulates in-memory counters into it, updates CPU usage and transient session/tcon/file counts, stores the full `profile_stats`, unlocks, clears in-memory counters, and flushes active per-service stats. Cleanup of an exited PID deletes its record, accumulates it into a destination summary record, fixes disconnect count to match connect count, clears transient counters, marks the result as a summary, and stores it.

Per-service profiling grows an array indexed by service number, creates DB keys containing service, PID, snum, and remote, increments/decrements refs as connections are made and released, returns a stats pointer for active services, stores active entries during dump, and deletes entries whose refcount has reached zero.

## State and Persistence

The primary persistent store is `smbprofile.tdb` in the cache directory. Keys are PID bytes for global worker records and string keys for per-service records. In-memory state includes active profiling config, pending stats, event/timer references, smbd connection pointer, and per-service table entries. Profile records include a magic value so readers ignore records from incompatible layouts.

## Dependencies and Integration Points

The file depends on Samba messaging, tevent timers, TDB wrap, profile read helpers, GnuTLS-derived magic from `profile_read.c`, `smbd_server_connection` counters, process IDs from tevent, and optional `getrusage()`. It integrates with smbcontrol/profile commands and smbd connection lifecycle.

## Risks and Edge Cases

- Profile layout changes require magic mismatch handling; stale records are zeroed/ignored.
- Chain-lock failures silently skip dumps or cleanup.
- Reset wipes the TDB and in-memory per-service stats, which is intentionally broad.
- Per-service DB keys include remote names and PIDs; uncontrolled string sizes are bounded only by allocation success.
- Transient counters must not be accumulated across worker cleanup; the code explicitly zeroes them in summary records.

## Test Signals

Tests should cover profile level toggles, request-level response, writable and read-only setup, magic mismatch filtering, dump accumulation with CPU/session counters, cleanup into summary records, per-service ref/store/delete behavior, and reset wiping both global and per-service state.
