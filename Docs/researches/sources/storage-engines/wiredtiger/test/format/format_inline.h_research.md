# sources/storage-engines/wiredtiger/test/format/format_inline.h

## Purpose
`format_inline.h` contains small, high-use inline helpers and trace macros shared by format workers. It wraps WiredTiger cursor/transaction/lock behavior with format-specific retry, timeout, RNG, table-selection, and tracing policy.

## Important APIs, Types, And Functions
Important helpers include `read_op`, `rng`, `mmrand`, `random_sleep`, `tables_apply`, `table_maxv`, `table_sumv`, `table_select`, `table_select_type`, `wt_wrap_open_cursor`, `table_cursor`, `wt_wrap_begin_transaction`, `key_gen`, `key_gen_insert`, and `lock_*` wrappers. It defines `FORMAT_PREPARE_TIMEOUT`, `trace_msg`, `trace_uri_op`, and `trace_op`.

## Control Flow
`read_op` dispatches cursor reads and waits out `WT_PREPARE_CONFLICT` until a 120-second timeout. RNG helpers centralize random choice and bounded random sleeps. Table helpers abstract single-table versus multi-table layout. Cursor open retries on metadata `EBUSY`. Transaction begin injects `operation_timeout_ms` and retries `WT_CACHE_FULL`. Lock wrappers dispatch to WiredTiger or pthread read-write locks according to `RWLOCK.lock_type`. Trace macros emit verbose messages and optional transaction snapshot details when trace flags are set.

## State And Persistence Behavior
The helpers mostly mutate in-memory session/cursor/lock state. `wt_wrap_begin_transaction` affects transaction state but does not commit. `table_cursor` lazily stores cursors in `TINFO`. Key generation writes caller-provided `WT_ITEM` buffers. No files are written directly.

## Dependencies And Integration Points
The header depends on `format.h` types and globals, WiredTiger internal lock/random/session APIs, and testutil assertions. It is included at the end of `format.h`, making its helpers available to all format source files.

## Risks And Test Signals
Risks include infinite waits if prepare conflicts do not resolve before timeout, biased or shared RNG use in the wrong operation class, cursor reuse mismatches when table IDs change, and lock-type initialization errors. Signals include prepare-conflict timeout assertions, `open_cursor` failures after `EBUSY` retry, transaction begin failures, and verbose trace output when flags are enabled.
