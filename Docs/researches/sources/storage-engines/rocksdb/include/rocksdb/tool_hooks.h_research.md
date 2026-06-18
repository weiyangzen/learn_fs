# Research: sources/storage-engines/rocksdb/include/rocksdb/tool_hooks.h

- **Purpose:** Provides a work-in-progress hook interface allowing `db_bench_tool` and similar tools to override how DB variants are opened and how the tool exits.
- **Important APIs/types/functions:** `ToolHooks` declares virtual `Open()` overloads for `DB`, column families, read-only DBs, `TransactionDB`, `OptimisticTransactionDB`, secondary/follower opens, and `blob_db::BlobDB`, plus `Exit(int)`. `DefaultHooks` implements the interface using normal RocksDB open calls and `exit(status)`. `defaultHooks` is the global default instance.
- **Control flow:** Tools call through a `ToolHooks` object instead of invoking static DB open methods directly. Custom subclasses can redirect opens to alternate implementations while preserving benchmark/tool call sites.
- **State and persistence:** The hooks do not own durable state by default, but open calls create DB handles and may create/read DB directories, WALs, blob files, and metadata.
- **Dependencies:** Depends on `rocksdb/db.h`, transaction DB forward declarations, and BlobDB types.
- **Integration points:** Primarily integrated with `db_bench_tool`; it bridges benchmarks to DB, transaction, secondary, follower, and BlobDB open paths.
- **Risks:** Marked work in progress and subject to change. Hooks must exactly mirror default semantics for options, CF handle ownership, error propagation, and process exit or benchmark behavior changes.
- **Test signals:** Tool tests should use custom hooks to assert the intended open overload is called, errors propagate, handles are returned/owned correctly, and `Exit()` is interceptable.
