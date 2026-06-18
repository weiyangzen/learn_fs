# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/SecondaryDBTest.java

## Purpose

This suite tests opening RocksDB in secondary mode from Java, both for the default column family and for explicit column-family descriptors. It verifies a secondary DB can read primary data and catch up to a selected point in primary WAL/manifest state.

## Important APIs and types

The file uses `RocksDB.openAsSecondary`, `tryCatchUpWithPrimary`, `Options`, `DBOptions`, `ColumnFamilyOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, and temporary primary/secondary directories.

## Control flow

Each test opens a primary DB, writes initial keys, then opens a secondary DB pointing at the primary path plus a separate secondary path. It asserts initial data is visible, writes more keys to the primary, invokes `tryCatchUpWithPrimary()`, and asserts only writes before the catch-up call are visible.

## State and persistence behavior

The tests rely on filesystem state in the primary DB directory and separate state in the secondary directory. Secondary reads are read-only and lag primary writes until explicit catch-up. Column-family handle lifetimes are carefully closed after use.

## Dependencies and integration points

This is a Java binding test for RocksDB secondary-instance recovery, WAL replay/catch-up, and column-family descriptor mapping.

## Risks and test signals

Risks include secondary accidentally seeing uncaught-up writes, incorrect CF handle mapping, and resource leaks from secondary handles. Signals are exact values for keys written before catch-up and `null` for the key written after catch-up.
