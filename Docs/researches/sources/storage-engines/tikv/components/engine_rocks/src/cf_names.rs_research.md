# sources/storage-engines/tikv/components/engine_rocks/src/cf_names.rs

Purpose: Implements column-family name discovery for `RocksEngine`.

Important APIs and types: `RocksEngine` implements `CfNamesExt::cf_names` by delegating to the inner RocksDB handle.

Control flow and state: Stateless delegation; returned names reflect the currently opened RocksDB column families.

Dependencies and integration: Used by compaction, maintenance, metrics, and callers that need to iterate all CFs. It depends on the local `RocksEngine::as_inner` API and RocksDB's CF-name access.

Risks: Lifetime and validity of returned `&str` values depend on the inner RocksDB wrapper contract. No filtering is applied.

Test signals: Indirectly exercised by compaction tests that iterate all CF names.
