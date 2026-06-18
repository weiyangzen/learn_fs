# sources/object-store/garage/src/table/lib.rs

Purpose: crate root for `garage_table`.

Important exports: declares public modules `schema`, `util`, `data`, `replication`, and `table`; private modules `gc`, `merkle`, `metrics`, `queue`, and `sync`; re-exports schema, table, and util APIs; and re-exports Garage CRDT utilities under `garage_table::crdt`.

Control flow: no runtime logic. The root also sets `recursion_limit = "1024"` and allows `clippy::comparison_chain`, likely for generated/complex generic code and existing style.

State and persistence: none directly. Persistence is implemented by `data`, `merkle`, `gc`, and workers in submodules.

Dependencies and integration: this is the public boundary consumed by Garage model tables and service crates. Private modules are still wired through `table.rs` and `data.rs` to provide replication, sync, GC, and metrics.

Risks and test signals: public re-exports shape downstream API compatibility. Keeping worker modules private limits direct external coupling. No direct tests.
