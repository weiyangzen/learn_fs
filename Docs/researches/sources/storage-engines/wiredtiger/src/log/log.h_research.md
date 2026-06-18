# sources/storage-engines/wiredtiger/src/log/log.h

## Purpose
`log.h` is the public/internal logging interface header shared across WiredTiger. It defines log scan/write/sync flags, the `WT_LSN` representation, on-disk `WT_LOG_RECORD` header layout, log format version gates, log manager state, printlog arguments, thread wrappers, and prototypes for the log subsystem and generated log operation codecs.

## Important APIs, Types, and Constants
- `WT_LSN`: 64-bit atomic union of `(file, offset)` used as the transaction log position. Macros such as `WT_ASSIGN_LSN`, `WT_SET_LSN`, `WT_INIT_LSN`, `WT_ZERO_LSN`, `WT_IS_INIT_LSN`, `WT_IS_ZERO_LSN`, and `WT_IS_MAX_LSN` centralize atomic updates and comparisons.
- `WT_LOG_RECORD`: on-disk record header with `len`, `checksum`, `flags`, zero padding, `mem_len`, and flexible payload. Flags currently persist compression and encryption.
- `WT_LOG_FILENAME`: base prefix for real log files.
- `WT_LOG_FILE_MIN/MAX`: configured size bounds.
- `WT_LOGSCAN_*`: scan behavior flags for first record, checkpoint start, one-record lookup, recovery, and metadata recovery.
- `WT_LOG_*`: transaction sync/write flags for dsync, flush, fsync, and sync-enabled mode.
- `WT_LOG_V*_VERSION`: WiredTiger release thresholds that map compatibility versions to log file versions.
- `WT_TXN_PRINTLOG_ARGS`: carries printlog output stream and flags for hex, messages-only, and unredacted output.
- `WT_LOG_THREAD`: condition/session/thread bookkeeping for log manager threads.
- `WT_LOG_MANAGER`: connection-global logging configuration and runtime state, including compressor, file sizes, path, txn sync mode, cursor count, preallocation counts, compatibility requirements, thread handles, and global log flags.
- Prototypes expose log cursor open, scan, write, flush, backup file collection, truncation, reset, manager config/create/open/destroy, generated log operation pack/unpack/print helpers, and inline LSN helpers.

## Control Flow Role
This header does not implement control flow, but it defines the contracts used by all log control paths:
- Writers and recovery code pass `WT_LSN` pointers through `log.c`, `txn_log.c`, and cursor code.
- `WT_LOG_RECORD` layout is assumed by generated operation packing (`log_auto.c`), physical write/read (`log.c`), and transaction printlog.
- `WT_LOG_MANAGER.flags` determines whether logging is configured, enabled, removable, recovering dirty, downgraded, failed, or zero-filled.
- Scan flags gate `__wt_log_scan` behavior and determine how invalid LSNs are reported.

## State and Persistence Behavior
- `WT_LSN` is intentionally atomically assigned as a 64-bit `file_offset` because compilers/sanitizers may not perform safe atomic struct assignment.
- `WT_LOG_RECORD` flags are explicitly not auto-generated because they are written to disk and cannot change meaning.
- The unused padding in `WT_LOG_RECORD` is expected to be zero and is checked for corruption by `log.c`.
- Version constants preserve compatibility with historic log formats and determine first-record layout and system-record availability.

## Dependencies and Integration Points
- Included by core WiredTiger internals through `wt_internal.h` and by log implementation files.
- Tied to generated prototypes from `prototypes.py`; changes require regeneration.
- Uses WiredTiger atomics, version structures, stream types, sessions, cursors, compressors, condition variables, rwlocks, and thread abstractions.
- Generated log operation functions declared here are implemented in `log_auto.c` and consumed by transaction logging, recovery, cursors, and printlog.

## Risks and Edge Cases
- On-disk constants (`WT_LOG_RECORD_*`, log version mapping, file naming) are compatibility-sensitive.
- Endianness of `WT_LSN` fields is handled through union layout and atomic loads; direct non-macro updates can break portability or TSAN assumptions.
- `WT_IS_MAX_LSN` intentionally accepts both `INT32_MAX` and `UINT32_MAX` offsets for older releases.
- `WT_LOG_MANAGER` mixes configuration, persistent-version policy, thread state, and counters, so initialization/destruction ordering is important.

## Test Signals
- ABI/on-disk format tests should detect accidental changes to `WT_LOG_RECORD` layout and flag values.
- Compatibility tests should validate `WT_LOG_V*_VERSION` mappings and startup bounds.
- Thread/concurrency tests should exercise atomic LSN assignment under log write and scan load.
- Printlog and cursor tests implicitly verify key/value formats `WTI_LOGC_KEY_FORMAT` and `WTI_LOGC_VALUE_FORMAT`.
