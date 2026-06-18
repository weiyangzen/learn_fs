# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MemoryUtil.java research

## Purpose

`MemoryUtil` is a static JNI facade for approximate RocksDB memory usage. It aggregates usage across supplied DB instances and caches and returns a Java map keyed by `MemoryUsageType`.

## Important APIs and types

`getApproximateMemoryUsageByType(List<RocksDB>, Set<Cache>)` accepts nullable DB and cache collections. It converts them to native handle arrays, calls native `getApproximateMemoryUsageByType(long[], long[])`, and converts the returned byte-keyed map to `Map<MemoryUsageType, Long>`.

## Control flow

The method computes counts, fills arrays by iterating the list and set, calls JNI once, then decodes each map key with `MemoryUsageType.getMemoryUsageType()`. Cache iteration uses an explicit index because sets do not expose indexed iteration.

## State and persistence behavior

The class owns no state. It samples process memory associated with live native handles. Results are approximate and transient; no DB files are modified.

## Dependencies and integration points

It depends on `RocksDB`, `Cache`, `MemoryUsageType`, and native memory-util code. It deliberately reports cache usage only for caches passed in the cache set, not caches reachable through the DB list.

## Risks and test signals

Risks include passing closed objects, duplicate caches collapsed by `Set`, and unknown native category bytes. Tests should cover null inputs, empty inputs, multiple DBs, shared caches, closed-handle behavior, and byte-to-enum conversion.
