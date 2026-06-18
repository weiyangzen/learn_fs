# sources/object-store/rustfs/crates/scanner/src/scanner_budget.rs

## Purpose

`scanner_budget.rs` implements per-cycle scanner budgets. It turns optional runtime limits for duration, object count, and directory count into a cancellation token that scanner traversal can observe. It also records the first budget reason that stopped a cycle.

## Important APIs, Types, and Functions

- `ScannerCycleBudgetConfig` contains optional `max_duration`, `max_objects`, and `max_directories`.
- `ScannerCycleBudgetReason` identifies `Runtime`, `Objects`, or `Directories` and maps to/from compact `u8` codes.
- `ScannerCycleBudget` contains:
  - A child `CancellationToken`.
  - An atomic reason code.
  - Configured limits.
  - Atomic counters for scanned objects and started directories.
- Main methods:
  - `new(parent, config) -> Arc<Self>` creates the child token and spawns a duration timer when needed.
  - `token()` clones the child token.
  - `budget_elapsed()` and `reason()` expose stop state.
  - `max_duration`, `max_objects`, `max_directories` expose configured limits for logging/metrics.
  - `try_start_directory()` increments directory starts and rejects/cancels once the limit is exceeded.
  - `record_object_scanned()` increments object count and cancels once the limit is reached.

## Control Flow

The budget starts uncanceled with reason code `BUDGET_REASON_NONE`. If a runtime duration is configured, `new` spawns a Tokio task that races parent cancellation, child cancellation, and `sleep(duration)`. If the sleep wins, it atomically records `Runtime` and cancels the child token.

Traversal code calls `try_start_directory` before entering directories and `record_object_scanned` after object scans. Directory budget allows exactly `max_directories` starts; the first attempt beyond the limit records `Directories`, cancels the child token, and returns false. Object budget cancels when the count reaches `max_objects`. `compare_exchange` ensures only the first budget reason wins if multiple limits are reached concurrently.

Dropping `ScannerCycleBudget` cancels the child token, which releases waiters without marking a budget reason.

## State and Persistence Behavior

Budget state is entirely in memory and per cycle. The child cancellation token is derived from the scanner parent token, so parent shutdown cancels budgeted work. No state is persisted by this module. `scanner.rs` reads the final reason for metrics and partial-cycle logging, while lower-level scanner traversal uses the token to stop work.

## Dependencies and Integration Points

- Uses `tokio::time::sleep` and `tokio_util::sync::CancellationToken`.
- Config is resolved in `runtime_config.rs`.
- `scanner.rs` creates a budget for each cycle and maps reasons to common metrics.
- `scanner_folder.rs` and `scanner_io.rs` observe the token and call directory/object budget methods while scanning.

## Risks and Edge Cases

- Counters use relaxed atomics; this is appropriate for budget telemetry/cancellation but not for exact cross-thread sequencing.
- Object budget cancels when `objects >= max_objects`, whereas directory budget rejects after `directories > max_directories`. That means object limit permits exactly N scanned objects and then cancels, while directory limit returns false for the N+1 start.
- Duration timer is a spawned task per budget. Dropping the budget cancels its token and should let the timer task exit, but excessive short-lived budgets still create task churn.
- Because only the first reason wins, later exceeded limits are not visible in metrics.

## Test Signals

Unit tests assert runtime duration cancels the child token and records `Runtime`, object budget cancels after reaching the configured limit, and directory budget rejects the first directory beyond the configured limit while recording `Directories`. `scanner.rs` adds tests for drop cancellation and metric reason/source mapping.
