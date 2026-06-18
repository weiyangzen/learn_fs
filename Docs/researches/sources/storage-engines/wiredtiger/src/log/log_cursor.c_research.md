# sources/storage-engines/wiredtiger/src/log/log_cursor.c

## Purpose
`log_cursor.c` exposes WiredTiger log records through a cursor interface opened with `log:`. It scans physical log records via `__wt_log_scan`, then presents each transaction operation as cursor key/value tuples for recovery helpers, diagnostic tools, and code such as `__wt_log_needs_recovery`.

## Important APIs and Functions
- `__wt_curlog_open`: allocates and initializes `WTI_CURSOR_LOG`, configures cursor methods, forces buffered records out, and takes a read lock preventing log removal while the cursor is open.
- `__curlog_logrec`: callback from `__wt_log_scan`; copies one physical log record, stores current/next LSN, reads record type, and initializes intra-record stepping for commit records.
- `__curlog_next`: advances within the current commit record or scans one more physical record with `WT_LOGSCAN_ONE`.
- `__curlog_search`: positions by LSN from the cursor key, ignoring the step counter for search.
- `__curlog_kv`: converts current record/operation into cursor key `(file, offset, step)` and value `(txnid, rectype, optype, fileid, opkey, opvalue)`.
- `__curlog_op_read`: unpacks supported row/column modify, put, and remove operations into operation key/value buffers; unknown operations return raw operation bytes in the value.
- `__curlog_compare`, `__curlog_reset`, `__curlog_close`: implement cursor comparison, reset, resource cleanup, lock release, and cursor counter decrement.

## Control Flow
1. Opening a log cursor allocates LSNs and scratch buffers, initializes key/value formats, calls generic cursor init, flushes active log slots if logging is live, and acquires `log_remove_lock` in read mode.
2. `next` uses existing `stepp` pointers while there are unconsumed operations in the current commit record. When exhausted, it calls `__wt_log_scan` from `next_lsn` for one physical record.
3. `__curlog_logrec` skips the physical log header, reads the record type, and for commit records reads the transaction id. Non-commit records are returned as whole-record payloads.
4. `__curlog_kv` increments `step_count`, peeks operation type/size, unpacks a logical operation when possible, and populates the cursor key/value.
5. Closing frees all scratch buffers and releases the removal read lock, allowing archived log files to be removed.

## State and Persistence Behavior
- Cursor state is in `WTI_CURSOR_LOG`: `cur_lsn`, `next_lsn`, copied `logrec`, operation buffers, stepping pointers, `step_count`, `rectype`, and `txnid`.
- The cursor does not persist state; it reads persistent log records and materializes copies into scratch buffers.
- A live cursor increments `conn->log_mgr.cursors` and holds `log->log_remove_lock`, preventing removal/truncation from deleting files being scanned.
- `search` treats the counter component as ignored and positions only by file/offset LSN.

## Dependencies and Integration Points
- Depends on `__wt_log_scan` from `log.c` and operation unpackers from `log_auto.c`.
- Uses key/value formats from `log_private.h` (`WTI_LOGC_KEY_FORMAT`, `WTI_LOGC_VALUE_FORMAT`).
- Used by recovery-adjacent logic, print/inspection paths, and `__wt_log_needs_recovery`.
- Integrates with generic WiredTiger cursor API macros and stats counters.

## Risks and Edge Cases
- The cursor only turns selected row/column put/modify/remove operations into logical keys/values; truncates and other operation types are returned as raw values.
- `next` treats a zero byte at `stepp` as zero-fill/end-of-record, matching padded record behavior.
- Holding the removal lock for long cursor scans can block log archival/removal.
- Search ignores step counter, so callers seeking a specific operation within one LSN must iterate after positioning.
- Raw-mode toggling around cursor get/set must restore cursor flags on all error paths.

## Test Signals
- Cursor tests should cover next/search/reset/compare/close and open cursor blocking log removal.
- Operation exposure tests should verify row and column put/modify/remove key/value formatting.
- Non-commit record tests should verify whole-record payload return with `WT_LOGOP_INVALID`.
- Boundary tests should cover end-of-log mapping from `ENOENT` to `WT_NOTFOUND`, padded zero bytes, and searching init/invalid/future LSNs through scan behavior.
