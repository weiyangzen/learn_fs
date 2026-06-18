# sources/storage-engines/wiredtiger/test/suite/test_tiered09.py

## Purpose
`test_tiered09.py` verifies that one database can reopen sequentially with different bucket prefixes while preserving each tiered object's original prefix metadata and remaining readable.

## Important APIs, Types, and Functions
The test uses `TieredConfigMixin`, `get_conn_config`, `get_check`, manual `wiredtiger_open`, and directory-store object checks. Key constants define expected object names for `table:test_tiered09` and `table:test_second09`.

## Control Flow
The test creates a table under the default prefix, writes data, forces `flush_tier`, closes, and checks directory-store bucket object placement. It removes local object copies, reopens with `bucket_prefix1`, creates a second table, updates the original table, forces another flush, closes, and verifies both prefixes in the bucket. After removing local copies again, it reopens with `bucket_prefix2` and verifies both tables can read all data.

## State and Persistence Behavior
The core persistence invariant is that object metadata stores the prefix used when each object was created, so later connection-level prefix changes must not change lookup paths for existing objects.

## Dependencies and Integration Points
It integrates with tiered connection config, manual reopen paths, bucket prefix configuration, local object deletion, and directory-store bucket naming.

## Risks and Test Signals
Risks include using the current connection prefix for historical object reads or losing pending local cleanup work across close. Signals are bucket file existence under expected prefixes and full cursor readback after prefix changes.
