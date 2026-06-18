# sources/storage-engines/sqlite/ext/fts5/fts5_storage.c

## Purpose

`fts5_storage.c` is the persistence layer that sits between the FTS5 virtual table front end and the index subsystem. It owns shadow-table SQL, content/docsize/config table creation and maintenance, totals/averages persistence, content insertion/deletion, rebuild, optimize/merge/reset wrappers, integrity checking against stored content, statement caching, and special handling for contentless and locale-aware tables.

## Important APIs, types, and functions

The central type is `Fts5Storage`, containing `Fts5Config`, `Fts5Index`, cached totals (`nTotalRow`, `aTotalSize`, `bTotalsValid`), a saved lookup statement for UPDATE no-change values (`pSavedRow`), and a small prepared-statement cache. Statement ids cover scans, lookups, content insert/replace/delete, docsize replace/delete/lookup, config replacement, and unrestricted scan.

Public entry points include `sqlite3Fts5StorageOpen()`, `sqlite3Fts5StorageClose()`, `sqlite3Fts5DropAll()`, `sqlite3Fts5StorageRename()`, `sqlite3Fts5CreateTable()`, `sqlite3Fts5StorageDelete()`, `sqlite3Fts5StorageDeleteAll()`, `sqlite3Fts5StorageRebuild()`, `sqlite3Fts5StorageOptimize()`, `sqlite3Fts5StorageMerge()`, `sqlite3Fts5StorageReset()`, `sqlite3Fts5StorageContentInsert()`, `sqlite3Fts5StorageIndexInsert()`, `sqlite3Fts5StorageIntegrity()`, `sqlite3Fts5StorageStmt()`, `sqlite3Fts5StorageStmtRelease()`, `sqlite3Fts5StorageDocsize()`, `sqlite3Fts5StorageSize()`, `sqlite3Fts5StorageRowCount()`, `sqlite3Fts5StorageSync()`, `sqlite3Fts5StorageRollback()`, and `sqlite3Fts5StorageConfigValue()`.

Important internal helpers are `fts5StorageGetStmt()` for lazy SQL preparation, `fts5StorageInsertCallback()` for writing token positions to the index during tokenization, `sqlite3Fts5StorageFindDeleteRow()` and `sqlite3Fts5StorageReleaseDeleteRow()` for saved-row update handling, `fts5StorageDeleteFromIndex()`, `fts5StorageContentlessDelete()`, `fts5StorageInsertDocsize()`, `fts5StorageLoadTotals()`, `fts5StorageSaveTotals()`, `fts5StorageNewRowid()`, and the integrity-check callback/termset code.

## Control flow

Open optionally creates shadow tables. Normal/contentless-unindexed tables get a `%_content` table with rowid, stored content columns, optional unindexed-only content columns, and optional locale columns for indexed columns. Tables with `columnsize=1` get `%_docsize`; contentless-delete tables add an `origin` column. All tables get `%_config`, initialized with the FTS5 version.

Inserts are split into content and index phases. `sqlite3Fts5StorageContentInsert()` writes or replaces `%_content` for normal/unindexed-content tables, decodes `fts5_locale()` blobs into text plus locale side columns, and reads unchanged UPDATE values from `pSavedRow`. For external or pure contentless tables it only chooses or allocates a rowid. `sqlite3Fts5StorageIndexInsert()` loads totals, begins an index write, tokenizes each indexed column with the current locale, writes each token through `sqlite3Fts5IndexWrite()`, accumulates per-column sizes into a varint `%_docsize` blob, updates totals, and stores docsize.

Deletes load totals, begin a delete index write, remove terms using either supplied values or a content lookup, decrement totals, write contentless-delete tombstones when applicable, then delete docsize and content rows. Rebuild clears index/docsize/unindexed content state, scans the content source, retokenizes every indexed column, rewrites docsize, and saves totals. Sync saves cached totals and calls index sync while preserving `last_insert_rowid`.

## State and persistence behavior

Persistent state is stored in FTS5 shadow tables `%_data`, `%_idx`, `%_config`, `%_docsize`, and sometimes `%_content`. `%_data`/`%_idx` are primarily maintained by the index subsystem, but this layer drops, clears, reinitializes, and syncs them. `%_config` stores version and runtime config values; changing a config value also increments the index cookie. `%_docsize` stores a varint array of per-column token counts, plus `origin` for contentless-delete. Totals are cached in memory during write transactions and serialized into the index averages record on sync.

`pSavedRow` is important for UPDATE semantics. When a row is being updated, FTS5 may need original content values for columns whose SQLite argument is `sqlite3_value_nochange()`, especially to preserve locale metadata. The storage layer keeps the lookup statement stepped on the old row until the subsequent content/index insert finishes, then resets it.

## Dependencies and integration points

This file depends on `fts5Int.h`, SQLite prepared statements and SQL execution, `sqlite3Fts5Tokenize()`, locale helpers from `fts5_main.c`, and many `sqlite3Fts5Index*` calls. It is called directly by `fts5_main.c` virtual table methods and indirectly by extension APIs such as xColumnSize, xColumnTotalSize, and xRowCount. It relies on `Fts5Config` generated SQL fragments such as `zContentExprlist`, `zContent`, `zContentRowid`, column counts, locale flags, content mode, and unindexed-column maps.

## Risks and edge cases

Prepared statement construction is mode-dependent and must match shadow-table schemas exactly. A missing internal shadow table is translated to `SQLITE_CORRUPT` for internal statements, while missing external content has different behavior. Totals can become corrupt if deletes see absent rows or docsize blobs decode incorrectly. Contentless-delete behavior depends on a valid origin from `%_docsize`. `columnsize=0` prevents automatic rowid allocation for external/contentless inserts. Locale storage is split between encoded values for external content and side columns for normal content, so UPDATE no-change paths must keep text and locale synchronized.

## Test signals

Primary test signals are `integrity-check` special inserts and SQLite `xIntegrity`, both of which call `sqlite3Fts5StorageIntegrity()`. The integrity path retokenizes content, verifies docsize counts, recomputes expected index checksums including prefixes and detail modes, checks content/docsize row counts, validates totals, and delegates final checksum comparison to the index layer. Rebuild, optimize, merge, delete-all, contentless-delete, locale, nochange UPDATE, and columnsize variations are all visible through this module.
