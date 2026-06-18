<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_shared_cache01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_shared_cache01.py

Purpose: exercises basic shared-cache behavior across multiple independent WiredTiger home directories and connections, including joining/leaving, full allocation, verbose output, default configs, mixed shared/non-shared connections, and invalid absolute eviction configuration.

Important APIs/types/functions: `test_shared_cache01` manually manages connections by overriding setup/close hooks. Helpers `openConnections`, `closeConnections`, and `add_records` use `wiredtiger_open`, `shared_cache=(name=pool,...)`, filesystem directory setup, sessions, and overwrite cursors.

Control flow: tests open two to four homes with a shared cache, create the same table in each, and insert data. Specialized cases fill the cache with repeated batches, add a late third connection, close one connection while others continue, check verbose output for pool creation, open one connection outside the pool, and exercise default shared-cache values.

State and persistence behavior: each home persists its own table, while cache quota and eviction settings are shared by pool name across connections. The test mostly validates configuration and operation completion rather than detailed persisted data reads.

Dependencies/integration points: integrates connection-level shared cache, eviction config validation, capture output, directory management, and multi-connection lifecycle. Risks include memory/runtime cost and global shared-cache side effects; signals are successful writes/closes and expected errors for absolute eviction thresholds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_shared_cache01.py -->
