# sources/storage-engines/wiredtiger/test/suite/test_error_info02.py

## Purpose

Exercises `get_last_error()` for `WT_ROLLBACK` sub-reasons: cache overflow, write conflicts, and oldest-pinned transaction eviction rollback.

## Important APIs, Types, and Functions

Defines `test_error_info02` with methods for cache overflow, update-list write conflict, timestamp visibility conflicts at start/stop, and oldest-for-eviction. It uses `error_info_util.assert_error_equal`.

## Control Flow

Each method creates a table and constructs a rollback source: tiny cache and eviction pressure, two sessions updating the same key, eviction of invisible disk updates, remove/insert conflicts, or an old transaction holding cache hostage. The caught public exception string is generic `WT_ROLLBACK`; the test then asserts the session's detailed sub-reason.

## State and Persistence Behavior

State spans concurrent sessions, transactions, read visibility, eviction-triggering cursors, and connection reconfiguration. Some tests switch `self.session` to the session that actually saw the error.

## Dependencies and Integration Points

Depends on `wiredtiger`, `time`, `wttest` skip hooks, and the error-info utility. It integrates transaction conflict handling, cache eviction, and rollback reason reporting.

## Risks and Maintenance Signals

The cache-overflow path is skipped for disaggregated mode and may depend on cache timing. Large values and sleeps can make runtime or flakiness sensitive to environment performance.

## Test Signals

Signals are exact sub-error constants `WT_CACHE_OVERFLOW`, `WT_WRITE_CONFLICT`, and `WT_OLDEST_FOR_EVICTION` after rollback-producing API calls.
