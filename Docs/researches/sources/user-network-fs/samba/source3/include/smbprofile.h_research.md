# sources/user-network-fs/samba/source3/include/smbprofile.h

## Purpose
`smbprofile.h` defines the source3 smbd profiling data model and macros. When `WITH_PROFILE` is enabled, it records counts, timings, byte totals, latency buckets, and per-service statistics into shared/TDB-backed profiling state; when disabled, the public macros collapse to no-ops.

## Important APIs, Types, and Macros
- Statistic catalog: `SMBPROFILE_STATS_ALL_SECTIONS` enumerates global loop, authentication, syscall, ACL, stat-cache, SMB1, Trans2, NT transact, and SMB2 operations.
- Data types: `smbprofile_stats_count`, `smbprofile_stats_time`, `smbprofile_stats_basic`, `smbprofile_stats_bytes`, `smbprofile_stats_iobytes`, their async state types, `profile_stats`, `profile_stats_persvc`, and `smbprofile_global_state`.
- Global state: `profile_p` and `smbprofile_state`.
- Instrumentation macros: `DO_PROFILE_INC`, `START_PROFILE`, `START_PROFILE_BYTES`, `END_PROFILE`, `END_PROFILE_BYTES`, `SMBPROFILE_*_ASYNC_*`, and per-share `_X` variants.
- Runtime functions: `smbprofile_dump_setup`, `smbprofile_dump_schedule_timer`, `smbprofile_dump`, `smbprofile_cleanup`, `smbprofile_stats_accumulate`, `smbprofile_collect_tdb`, `smbprofile_collect`, `set_profile_level`, and `profile_setup`.
- Per-service functions under `WITH_PROFILE`: `smbprofile_persvc_mkref`, `smbprofile_persvc_unref`, `smbprofile_persvc_get`, `smbprofile_persvc_reset`, and collection helpers.

## Control Flow and State
Instrumentation starts by allocating an async state on the stack and recording a monotonic microsecond timestamp when counting/timing is enabled. End macros add elapsed time, idle time, byte totals, failed counts, and latency buckets, then call `smbprofile_dump_schedule`. Dump scheduling avoids repeated timer setup by checking `smbprofile_state.internal.te`. `smbprofile_update_failed_count` treats several protocol statuses as successful for specific SMB2 opcodes, and `smbprofile_update_hist` increments cumulative latency buckets.

## Persistence Behavior
Profiling data is kept in process/global structures and integrated with a TDB-backed dump/collection path via `tdb_wrap`. Per-service records include service number, reference count, active flag, and flexible `dbkey[]`. The header declares cleanup and collection but leaves actual TDB persistence to profile implementation files.

## Dependencies and Integration Points
The file depends on `replace.h`, `tdb.h`, time utilities, SMB2 opcode constants, and NTSTATUS utilities. It is included by `vfs.h`, and its macros are used across smbd syscall wrappers, SMB request handlers, authentication, VFS operations, and profile-control messaging.

## Risks
- Macro instrumentation must pair start/end variables exactly; mismatched names or early returns can lose timings.
- Shared/global counters are performance-sensitive and may be touched in hot paths.
- Disabled-profile no-op macros must preserve compile compatibility and avoid evaluating expensive arguments unexpectedly.
- Latency bucket logic is cumulative; consumers must interpret bucket counts correctly.

## Test Signals
Builds with and without `WITH_PROFILE`, smbd profile level changes, `smbstatus`/profile collection behavior, SMB2 failed-count exceptions, per-share profile reference/unref tests, and leak/race checks around scheduled dumps are strong signals.
