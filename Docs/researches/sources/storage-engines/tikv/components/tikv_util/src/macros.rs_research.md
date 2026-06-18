# sources/storage-engines/tikv/components/tikv_util/src/macros.rs

## Purpose
Defines general-purpose exported macros for error boxing, slow logging, inherited thread names, scope defer, callback waiting, option/result propagation, panic safety, and display delegation.

## Important APIs, Types, And Functions
`box_err!` creates a boxed error including source file and line. `box_try!` returns early with a boxed error. `slow_log!` logs slow-operation warnings, either from a timer-like value (`T` arm) or a duration. `thd_name!` appends inherited thread tags. `defer!` creates a `DeferContext`. `wait_op!` runs an async callback-style operation and waits on an mpsc receiver with optional timeout. `try_opt!` and `try_opt_or!` simplify `Result<Option<T>>` propagation. `safe_panic!` logs instead of panicking during unwind. `impl_format_delegate_newtype!` and `impl_display_as_debug!` implement `Display`.

## Control Flow
Most macros expand to direct control flow at call sites. `wait_op!` creates a channel, passes a boxed callback into the expression, propagates expression errors with `?`, then blocks waiting for a result or timeout. `safe_panic!` checks `std::thread::panicking`; during unwind it emits an error log with a double-panic-prevented suffix, otherwise it calls `panic!`.

## State And Persistence
Macros have no owned state. Expanded code may create channels, defer guards, boxed errors, or log records.

## Dependencies And Integration
Depends on crate logging macros, `logger::LogCost`, time conversion helpers, `DeferContext`, and `get_tag_from_thread_name`. These macros are exported at crate root and used throughout TiKV.

## Risks
`box_err!` captures call-site line numbers, so tests and diagnostics are line-sensitive. `wait_op!` blocks the current thread and assumes the expression accepts a callback and returns `Result`. `safe_panic!` avoids aborting on double panic but only logs if the logger is usable during unwinding.

## Test Signals
Tests verify `box_err!` includes the expected file/line text and that `safe_panic!` in a `Drop` implementation does not double-panic during an existing unwind.
