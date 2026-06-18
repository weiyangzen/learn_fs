# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MemoryUsageType.java research

## Purpose

`MemoryUsageType` names the categories returned by RocksDB approximate memory-usage reporting. It maps native byte keys to Java enum constants for memtables, table readers, and caches.

## Important APIs and types

The constants are `kMemTableTotal`, `kMemTableUnFlushed`, `kTableReadersTotal`, `kCacheTotal`, and `kNumUsageTypes`. `getValue()` returns the native byte. `getMemoryUsageType(byte)` decodes bytes and throws for unknown values.

## Control flow

`MemoryUtil` receives a native `Map<Byte, Long>` and decodes every key through `getMemoryUsageType()`. Unknown bytes fail the call rather than being silently ignored.

## State and persistence behavior

The enum stores immutable native category IDs. It reports memory state only; it has no persistence behavior.

## Dependencies and integration points

It integrates with `MemoryUtil.getApproximateMemoryUsageByType(...)` and the native `rocksdb::MemoryUtil` category ordering.

## Risks and test signals

The key risk is native enum drift or introduction of a new category without Java updates. Tests should cover all known byte mappings, invalid-byte rejection, and non-empty memory reports for DBs and caches.
