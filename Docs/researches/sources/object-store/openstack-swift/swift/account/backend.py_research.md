# sources/object-store/openstack-swift/swift/account/backend.py

## Purpose
Implements Swift's account database broker. `AccountBroker` encapsulates SQLite schema creation, container record merging, account/global stats, policy stats, listing semantics, deletion detection, and legacy schema migrations.

## Important APIs, Types, and Functions
`DATADIR = 'accounts'` identifies the on-disk account DB directory. `POLICY_STAT_TRIGGER_SCRIPT` defines triggers keeping `policy_stat` in sync with container inserts/deletes. `AccountBroker` extends `DatabaseBroker` and sets account DB metadata fields.

Schema methods are `_initialize`, `create_container_table`, `create_account_stat_table`, `create_policy_stat_table`, and `get_db_version`. Data APIs include `_commit_puts_load`, `put_container`, `merge_items`, `make_tuple_for_pickle`, `empty`, `get_info`, `get_policy_stats`, `list_containers_iter`, `_is_deleted`, `_is_deleted_info`, `is_status_deleted`, `_populate_instance_cache`, and `path`. Migration helpers are `_migrate_add_container_count` and `_migrate_add_storage_policy_index`.

## Control Flow
Creating a new DB validates that `self.account` is set, creates the container table plus triggers, initializes account stats, and creates policy stats. Container updates are append/merge oriented: `put_container` creates a record and delegates to `put_record`; `merge_items` deletes old active/deleted rows for the container and inserts the winning record after timestamp comparison.

Listing commits pending puts, builds SQL based on marker/end_marker/prefix/delimiter/reverse flags, handles reserved names, works around legacy schema differences, and synthesizes subdir rows when delimiter grouping is requested. Policy stats reads attempt the modern schema, then migrate or degrade gracefully when older DBs lack `container_count`, `policy_stat`, or `storage_policy_index`.

## State and Persistence Behavior
State is a SQLite account DB containing `container`, `account_stat`, and `policy_stat` tables plus triggers. `container_insert` and `container_delete` update aggregate account stats and hash; policy triggers update per-policy counts/bytes. `incoming_sync` is updated during replication merges with source sync points. Deletion state is derived from `status = DELETED` or delete timestamp newer than put timestamp with zero containers.

## Dependencies and Integration Points
Depends on `sqlite3`, `Timestamp`/`NormalTimestamp`, `DatabaseBroker`, `zero_like`, and `RESERVED_BYTE`. It integrates with account server request handling, account replicator, auditor, reaper, and any code that lists containers or reads account totals.

## Risks and Edge Cases
Triggers make aggregate correctness dependent on insert/delete discipline; direct updates are forbidden by trigger. Legacy migration paths are complex and must preserve stats while adding storage policy support. `merge_items` timestamp conflict logic is critical for replication convergence. Delimiter listing logic mutates markers in subtle ways, especially with reverse listings. Reserved-byte filtering can hide internal namespace entries unless explicitly allowed. Schema migrations during reads can surprise callers if DB permissions/locking are constrained.

## Test Signals
Expected tests should cover schema creation, policy stat migrations, merge conflict resolution, listings with marker/prefix/delimiter/reverse/reserved names, deletion detection, and auditor total validation. This file itself has no tests, but `auditor.py`, `reaper.py`, and account-server behavior depend on it.
