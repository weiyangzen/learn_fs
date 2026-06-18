## sources/storage-engines/pebble/tool/make_test_find_db.go

Purpose: build-tagged generator for the `find-db` fixture used by `find` tests.

Important APIs/types/functions: local `db` wraps `*pebble.DB`, comparer, and merger. `open` configures an alternate comparer, test merger, archive cleaner, logging event listener, VFS, and `FormatFlushableIngest`. Methods wrap Pebble operations: `set`, `merge`, `delete`, `singleDelete`, `deleteRange`, `ingest`, `flush`, `compact`, `snapshot`, and `close`. `ingest` writes a temporary SST using matching comparer/merger and ingests it.

Control flow: `main` removes `tool/testdata/find-db`, opens a new DB, writes point sets and merges, flushes and compacts, holds snapshots to pin data, ingests SSTs, compacts, writes deletes/single deletes/range deletes, flushes, and compacts again.

State and persistence: writes a complete Pebble DB fixture with current and archived WAL/SST/MANIFEST/OPTIONS files. Snapshots intentionally influence compaction output and retained history.

Dependencies and integration: uses Pebble DB APIs, SSTable writer, object-storage file writable, VFS, default comparer clone, and test merger. The generated fixture is consumed by `find.go` through datadriven tests.

Risks: fixture output depends on Pebble format/version behavior, compaction choices, event listener side effects, and relative working directory. The temp ingest file path is fixed and removed only by DB ingest/cleanup behavior.

Test signals: creates coverage for `find` over WAL records, flushed records, ingested tables, compaction provenance, archived files, point mutations, merges, single deletes, and range deletes.
