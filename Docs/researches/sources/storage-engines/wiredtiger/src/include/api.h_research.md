# sources/storage-engines/wiredtiger/src/include/api.h

## Purpose
This header defines the macro framework used by WiredTiger public connection, session, and cursor APIs. The macros standardize entry/exit bookkeeping, configuration validation, error-state handling, operation timing, transaction wrapping, retry-on-rollback behavior, overload rejection, and cursor-specific invariants.

## Important APIs, Types, And Functions
The base stack macros are `API_SESSION_PUSH`, `API_SESSION_POP`, and `API_SESSION_INIT`. `API_CALL`, `API_CALL_NOCONF`, and `API_CALL_NOCONF_NOERRCLEAR` wrap general entry points, while `API_END` unwinds the session and reconciles the return value with `session->err_info`. `TXN_API_CALL`, `TXN_API_CALL_NOCONF`, and `TXN_API_END` add autocommit transaction handling and optional rollback retry. Convenience wrappers cover connection calls, session calls that allow or reject prepare context, cursor calls, cursor update/remove calls, API stats, not-found mapping, retryable readonly APIs, cursor reposition windows, and compiled configuration setup.

## Control Flow
An API function enters by pushing the current dhandle/name, incrementing `api_call_counter`, setting `lastop`, checking panic state, starting single-thread and operation tracking, resetting wait/error state for outermost calls, clearing the global error log for external calls, and optionally validating configuration. Exit through `API_END` ends operation tracking, stops single-thread checks, optionally records transaction errors, normalizes `err_info`, stops operation timers, checks that too many HS cursors are not left open, and pops the saved session fields.

Transactional wrappers mark autocommit/update state when the caller is not already in a transaction. `TXN_API_END` either retries rollback, commits successful implicit transactions, or rolls back and resets cursors on error. Cursor update wrappers also check write overload and in-memory cache-full behavior. Read cursor wrappers can reject user reads under load control.

## State And Persistence Behavior
The macros mutate session runtime state: `dhandle`, `name`, `lastop`, `api_call_counter`, `cache_wait_us`, `err_info`, transaction flags, operation timers, cursor cached/reposition flags, and load-control statistics. They do not directly persist data, but they decide whether API operations commit, roll back, retry, return `WT_ROLLBACK`, map `WT_NOTFOUND` to `ENOENT`, or report errors into transaction state.

## Dependencies And Integration Points
This header depends on session, transaction, config, stats, load-control, cursor, and error-log helpers. It is included by API implementation files and defines the control skeleton those functions rely on. Because the macros open `do { ... } while` scopes and introduce local variables such as `__set_err`, `__autotxn`, and `__update`, callers must structure labels and `goto err` paths exactly around them.

## Risks
Macro ordering is the main risk. Code before `API_SESSION_INIT` or after `API_END` can break error handling. Missing an exit macro leaves counters, dhandles, timers, or transaction flags inconsistent. Nested API calls make `api_call_counter` behavior subtle, especially for error reset, operation timers, HS cursor assertions, and retry loops. Since these are macros, local variable name collisions and control-flow surprises are possible.

## Test Signals
API tests should cover nested calls, successful and failing config validation, panic checks, `WT_NOTFOUND` mapping, err_info synchronization, autocommit commit/rollback/retry, prepare-context rejection, load-control read/write rejection, cursor cache reuse, cursor reposition flags, in-memory cache-full updates, and leak checks for API counters and cursor/session state after errors.
