# sources/object-store/garage/src/table/data.rs

Purpose: local persistent data engine for one logical Garage table. It owns DB trees, read helpers, transactional mutation logic, insert queueing, Merkle todo updates, schema hooks, and GC todo scheduling.

Important APIs and types: `TableData<F, R>` stores `System`, schema instance, replication policy, main `store`, `merkle_tree`, `merkle_todo`, `insert_queue`, `gc_todo`, notifications, and metrics. Key methods include `new`, `read_entry`, `read_range`, `update_many`, `update_entry`, `update_entry_with`, `delete_if_equal`, `delete_if_equal_hash`, `queue_insert`, `tree_key`, and `decode_entry`.

Control flow: reads use `partition_key.hash() + sort_key` DB keys and range scans constrained by the partition hash prefix. Mutations run in DB transactions: decode old value, compute merged/new value, encode/migration-normalize it, write `merkle_todo`, write store, and call schema `updated`. After commit, changed tombstones may be inserted into `gc_todo` only if this node is first replica for the partition. Deletes are compare-and-delete operations that also enqueue empty Merkle todos and call schema hooks.

State and persistence: opens five persistent trees per table: `<table>:table`, `:merkle_tree`, `:merkle_todo`, `:insert_queue`, and `:gc_todo_v2`. Notifications wake background workers after commits.

Dependencies and integration: used by `Table`, `MerkleUpdater`, `InsertQueueWorker`, `TableGc`, and `TableSyncer`. Depends on CRDT merge, schema migration, replication node selection, and Garage DB transactions.

Risks and test signals: transaction boundaries are critical; missing Merkle todo or schema hook would corrupt sync/index behavior. The tombstone leader comment notes layout changes may break GC leadership assumptions. Decode failures are hexdumped. Tests are indirect via table users.
