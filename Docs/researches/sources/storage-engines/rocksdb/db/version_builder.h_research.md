# sources/storage-engines/rocksdb/db/version_builder.h

## Purpose

`version_builder.h` declares the version-building abstraction used to apply manifest edits to a base RocksDB version efficiently. It exposes normal builder operations, point-in-time recovery helpers, savepoint support, table-handler loading, and an RAII wrapper that keeps the base `Version` referenced while the builder is alive.

## Important APIs, Types, and Functions

`VersionBuilder` is constructed from file options, immutable CF options, table cache, base storage, version set, optional file metadata cache reservation manager, optional `ColumnFamilyData`, optional `VersionEditHandler`, and flags for found/missing file tracking and incomplete-version acceptance. Public methods include `CheckConsistencyForNumLevels`, `Apply`, `SaveTo`, `LoadTableHandlers`, `CreateOrReplaceSavePoint`, `ValidVersionAvailable`, `HasMissingFiles`, `GetAndClearIntermediateFiles`, `ClearFoundFiles`, `SaveSavePointTo`, `LoadSavePointTableHandlers`, and `ClearSavePoint`. `BaseReferencedVersionBuilder` has constructors for current or explicit base versions and exposes `version_builder()`.

## Control Flow

Callers typically create a builder with a referenced base version, call `Apply` for one or more edits, optionally validate availability in point-in-time mode, load table handlers for new files, and `SaveTo` a destination `VersionStorageInfo`. Savepoints move the current `Rep` into `savepoint_` and continue from a copied representation, enabling callers to preserve an earlier valid state while applying more edits.

## State and Persistence Behavior

The header hides implementation state behind `class Rep`. Persistent effects are indirect: saved storage later becomes the in-memory representation of MANIFEST state; table-handler loading may open SSTs and pin readers; PIT helpers track missing/intermediate file names for recovery cleanup. The wrapper's destructor unrefs the base version and therefore can trigger cleanup of old version resources.

## Dependencies and Integration Points

Dependencies include `version_edit`, file system options, metadata, slice transforms, `TableCache`, `VersionStorageInfo`, `VersionSet`, `VersionEditHandler`, `ColumnFamilyData`, and cache reservation management. Manifest readers, DB open, recovery, and secondary instance tailing use this interface.

## Risks and Test Signals

Risks include using the builder after the base version/storage has been destroyed, calling PIT-only APIs when tracking is disabled, saving a savepoint that is invalid or missing, and forgetting the DB mutex requirement around `BaseReferencedVersionBuilder`. Tests should cover constructor variants, repeated savepoint replacement, invalid savepoint status, current-version ref/unref balance, incomplete-version flags, and table-handler loading through savepoints.
