# sources/storage-engines/wiredtiger/test/suite/test_tiered03.py

## Purpose
`test_tiered03.py` is intended to test sharing tiered data between a primary and secondary database using block-log-structured/tiered configuration, but its only test is currently skipped.

## Important APIs, Types, and Functions
`test_tiered03` uses `TieredConfigMixin`, `get_conn_config`, `SimpleDataSet`, and quick scenarios for record count. `conn_config` customizes the bucket and cache directory, using an absolute bucket path for the directory store so multiple connections can share it.

## Control Flow
The skipped `test_sharing` would populate a primary file, checkpoint it, create a `SECONDARY` home, copy metadata into a writable metadata cursor under a relative URI, read the original checkpoint from the secondary, update the primary, extract the new checkpoint string from metadata, alter the secondary metadata, and verify the new data.

## State and Persistence Behavior
The intended state model is two WiredTiger homes sharing the same tiered bucket while using distinct local cache directories. Metadata checkpoint strings are the persistence boundary that lets the secondary advance from an older object view to a newer one.

## Dependencies and Integration Points
It integrates with metadata cursors, `session.alter`, secondary connection creation, regular expressions for checkpoint metadata extraction, and tiered storage source configuration.

## Risks and Test Signals
The explicit skip states that sharing the checkpoint file containing transaction ids is unsupported. If re-enabled, risks include metadata string parsing, relative URI correctness, cache isolation, and checkpoint consistency across homes.
