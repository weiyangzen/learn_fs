# sources/storage-engines/wiredtiger/test/suite/test_error_info04.py

## Purpose

Ensures successful commit and rollback calls that are pulled into eviction do not accidentally persist internal eviction errors into `get_last_error()`.

## Important APIs, Types, and Functions

Defines `test_error_info04`, a low-cache/dirty-eviction connection config, and two tests: `test_commit_transaction_skip_save` and `test_rollback_transaction_skip_save`.

## Control Flow

Each test opens 100 sessions, inserts large values in active transactions, lowers `cache_max_wait_ms`, then commits or rolls back all transactions. After every successful transaction end it asserts the last error is success (`0`, `WT_NONE`).

## State and Persistence Behavior

State includes many concurrent sessions with large dirty updates and connection-level eviction pressure. The intended persistence behavior is negative: successful transaction APIs must reset/keep last-error success despite eviction participation.

## Dependencies and Integration Points

Depends on `wiredtiger`, `error_info_util`, and transaction/cache reconfiguration paths.

## Risks and Maintenance Signals

The workload assumes 100 large transactions reliably trigger application eviction. It validates the session-level `get_last_error` view used by the inherited utility, not every temporary eviction sub-error internally generated.

## Test Signals

Signals are successful commit/rollback return codes and immediate `WT_NONE` last-error assertions under eviction pressure.
