# sources/storage-engines/wiredtiger/test/suite/test_tiered10.py

## Purpose
`test_tiered10.py` tests simultaneous WiredTiger homes sharing one bucket directory with different prefixes and identical table names.

## Important APIs, Types, and Functions
`test_tiered10` uses `TieredConfigMixin`, `get_conn_config`, `extensionsConfig`, manual `wiredtiger_open`, and `get_check`. `conn_config` creates two database directories and returns a dummy base connection while preparing a shared saved config.

## Control Flow
The test opens two independent connections in `first_dir` and `second_dir`, both using the same bucket but different `bucket_prefix` values. Each creates `table:test_tiered10`, writes distinct key ranges, forces `flush_tier`, and verifies expected bucket objects for directory store. Both connections close, local object files are removed, connections reopen with the same parameters, and each table is verified against its own data.

## State and Persistence Behavior
The state surfaces are two local homes, one shared bucket, and prefix-disambiguated object names. Removing local objects forces reads through shared storage or cache on reopen.

## Dependencies and Integration Points
It integrates with extension loading, relative bucket paths from subdirectories, tiered object naming, and multi-home connection management.

## Risks and Test Signals
The main risk is cross-home object collision when table URIs and object base names are identical. Signals are two distinct bucket objects and correct readback from both reopened connections.
