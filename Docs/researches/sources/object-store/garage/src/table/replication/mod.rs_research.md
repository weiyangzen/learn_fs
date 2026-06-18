# sources/object-store/garage/src/table/replication/mod.rs

Purpose: module root for table replication strategies.

Important exports: declares private `parameters`, `fullcopy`, and `sharded` modules, and re-exports `TableFullReplication`, all parameter traits/types, and `TableShardedReplication`.

Control flow: no runtime logic. It centralizes the replication public API for `garage_table`.

State and persistence: none directly.

Dependencies and integration: consumed by `data`, `table`, `sync`, `gc`, and Garage table definitions. The split keeps the trait contract separate from concrete full-copy and sharded implementations.

Risks and test signals: public re-export changes affect downstream imports. No direct tests.
