# sources/storage-engines/wiredtiger/src/log/log_inline.h

## Purpose
`log_inline.h` provides small inline helpers for endian conversion of log descriptors/records, atomic LSN access/comparison/stringification, and a race-avoiding preallocation-enabled check. These are hot-path or header-layout utilities shared by log implementation files.

## Important APIs and Functions
- `__wti_log_desc_byteswap`: byte-swaps `WTI_LOG_DESC` fields on big-endian hosts.
- `__wti_log_record_byteswap`: byte-swaps persisted `WT_LOG_RECORD` header fields on big-endian hosts.
- `__wt_log_cmp`: compares two `WT_LSN` values by reading each 64-bit atomic `file_offset` once.
- `__wt_lsn_string`: formats an LSN into `file,offset`.
- `__wt_lsn_file`, `__wt_lsn_offset`: atomically read individual file and offset components.
- `__wti_log_is_prealloc_enabled`: checks `log_mgr.prealloc_init_count` instead of the live adaptive `prealloc` counter to avoid concurrent read/write races.

## Control Flow Role
The inline functions are used throughout write, scan, sync, cursor, and manager code:
- Before checksumming/writing and after reading persisted headers, `log.c` calls the byteswap helpers to keep disk format little-endian.
- Slot release, scan range handling, sync waits, cursor comparison, and backup filtering call `__wt_log_cmp`.
- File and offset accessors are used wherever LSN components are reported or passed into cursor keys.
- Manager/server code uses `__wti_log_is_prealloc_enabled` to decide whether preallocation work is configured.

## State and Persistence Behavior
- Byteswap helpers define the endian boundary for persisted log descriptor and record headers.
- `__wt_log_cmp` deliberately snapshots each LSN once to avoid inconsistent comparisons when another thread updates an LSN concurrently.
- Preallocation enabled state is based on the initial configured count, not the adaptive count that changes while the log server runs.

## Dependencies and Integration Points
- Includes `log_private.h` for private structures and uses `WT_LOG_RECORD`, `WTI_LOG_DESC`, `WT_LSN`, session/connection macros, atomics, `WT_READ_ONCE`, and formatting helpers.
- Called by `log.c`, `log_mgr.c`, and `log_cursor.c`.

## Risks and Edge Cases
- Any new fields in `WTI_LOG_DESC` or `WT_LOG_RECORD` must update the corresponding byteswap helper.
- Direct LSN field reads elsewhere can bypass the one-read comparison discipline and introduce races.
- `__wt_lsn_string` asserts with a NULL session, so the assert mechanism must tolerate that use.
- Preallocation semantics depend on `prealloc_init_count` remaining immutable after configuration.

## Test Signals
- Big-endian or simulated endian tests should verify descriptor and record header round trips.
- Concurrency tests should exercise LSN comparison while writers advance `alloc_lsn`, `write_lsn`, and `sync_lsn`.
- Reconfiguration/preallocation tests should verify adaptive `prealloc` changes do not disable configured preallocation checks.
