# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MemTableConfig.java research

## Purpose

`MemTableConfig` is the abstract base for Java configuration objects that create native RocksDB memtable factories. It lets Java users select alternative in-memory write-buffer representations through `Options.setMemTableConfig(...)`.

## Important APIs and types

The only method is protected abstract `newMemTableFactoryHandle()`, which subclasses implement to return a native `MemTableRepFactory` handle. The class itself owns no native resource.

## Control flow

Applications instantiate a concrete subclass, pass it to `Options.setMemTableConfig`, and `Options` calls `newMemTableFactoryHandle()` to install the native factory.

## State and persistence behavior

Subclasses may store configuration fields, but this base has none. Memtable factory choice affects in-memory write buffering and flush behavior; persistence happens when native RocksDB flushes memtables into SSTs.

## Dependencies and integration points

It integrates with `Options`, native memtable factory creation, and concrete configs such as skip-list, vector, hash-linked-list, or hash-skip-list configurations elsewhere in the package.

## Risks and test signals

The main risks are native handle lifetime and invalid subclass parameters. Tests should assert that each concrete config installs successfully, reports the expected `memTableFactoryName()`, and can open/write/flush a DB.
