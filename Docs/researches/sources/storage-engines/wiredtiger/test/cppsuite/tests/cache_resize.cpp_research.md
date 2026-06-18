# sources/storage-engines/wiredtiger/test/cppsuite/tests/cache_resize.cpp

## Purpose
Tests behavior while the WiredTiger connection cache size alternates between very small and large values, and records enough tracker state for custom validation of accepted transactions.

## Important APIs, Types, And Functions
`operation_tracker_cache_resize` overrides `set_tracking_cursor` to write timestamp, transaction id, operation type, and cache size. `class cache_resize : public test` overrides `custom_operation`, `insert_operation`, and `validate`.

## Control Flow
The custom operation alternates `WT_CONNECTION::reconfigure` between `cache_size=1MB` and `cache_size=500MB`, reads the internal `conn_impl->cache_size`, and records a custom operation with the new cache size. Insert operation writes random keys into the last collection with the current cache size as the value, relying on transaction acceptance/rejection under cache pressure. Validation scans the operation tracking table, accepts only `CUSTOM` and `INSERT` operation types, skips cache-change rows, groups inserts by transaction id, and currently asserts only that at least one insert record exists.

## State And Persistence Behavior
The test mutates connection cache configuration and persists insert rows. The custom tracker uses internal WiredTiger session/connection structs to capture transaction id and cache size atomically with tracked operations. Several intended cache-size assertions are disabled by `FIXME-WT-12931`.

## Dependencies And Integration Points
Depends on constants/logger/random generator, `operation_tracker`, base test, `connection_manager`, and WiredTiger internal implementation structs `WT_SESSION_IMPL` and `WT_CONNECTION_IMPL`.

## Risks And Test Signals
This test reaches into internal WiredTiger structs, making it sensitive to implementation changes. Validation currently has weakened checks due to WT-12931, so its main signal is that tracked insert records exist and tracking format is parseable. Saving cache reconfiguration rows can itself roll back under pressure and is logged as a warning.
