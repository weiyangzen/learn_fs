# sources/storage-engines/rocksdb/utilities/option_change_migration/option_change_migration.cc

## Purpose
This file implements `OptionChangeMigration()`, a utility that rewrites/compacts an existing DB so it can be reopened safely after changing compaction style or level-related options, including multi-column-family configurations.

## Important APIs, types, and functions
`GetNoCompactionOptions()` disables automatic compaction and stalls by setting high L0 triggers and zero pending compaction byte limits.

`CompactToLevel()` compacts a CF to a target level using `CompactRangeOptions::change_level`; when target is L0 it forces bottommost compaction to avoid trivial move behavior.

`MigrateToUniversal()`, `MigrateToLevelBase()`, and `MigrateToFIFO()` decide compaction targets for target compaction styles. Universal compacts down only if existing highest level is outside new `num_levels`; level compacts to L1 for non-dynamic or last level for dynamic; FIFO compacts to L0.

`MigrateSingleColumnFamily()` dispatches based on old/new compaction style and treats old FIFO as no-op. `ValidateCFDescriptors()` requires old/new CF descriptor counts, names, and order to match.

`DetermineBaseOptions()`, `ApplySpecialSingleLevelSettings()`, and `PrepareNoCompactionCFDescriptors()` build temporary CF descriptors that can open the DB without unwanted compaction while still being close enough to new settings to rewrite metadata when needed.

`OpenDBWithCFs()`, `CleanupCFHandles()`, and `MigrateAllCFs()` manage DB opening, handle cleanup, and per-CF migration. Public overloads accept either full DB/CF descriptors or single `Options`.

## Control flow
The public multi-CF function validates descriptors, prepares no-compaction descriptors and tracks whether manifest-rewrite reopen is needed, opens the DB with old DB options and temporary CF options, migrates all CFs, destroys non-default CF handles, optionally closes and reopens with temporary descriptors to rewrite manifest state, then closes the DB.

## State and persistence behavior
The utility mutates persistent DB state by running compactions and rewriting manifest/options metadata through DB open/close. It does not add or drop CFs. Temporary in-memory vectors track handles and descriptors; handle cleanup is explicit.

## Dependencies and integration points
It depends on `rocksdb/utilities/option_change_migration.h` and `rocksdb/db.h`. It integrates with RocksDB compaction APIs, DB open/close, column family descriptors, and DB option/CF option conversion.

## Risks and edge cases
Adding, dropping, or reordering CFs is unsupported and rejected. Old FIFO is treated as no-op regardless of target style, which relies on FIFO layout already being acceptable. Cleanup errors can override success. The function opens with `old_db_opts` even for reopen steps using temporary CF descriptors, so DB-level option migration is limited. Very large sentinel values for file size/compaction bytes are magic constants.

## Test signals
`option_change_migration_test.cc` heavily covers compaction-style transitions, dynamic level changes, FIFO size limits, compaction with bottommost files, multi-CF migration, mixed target styles per CF, validation failures, and FIFO source migration.
