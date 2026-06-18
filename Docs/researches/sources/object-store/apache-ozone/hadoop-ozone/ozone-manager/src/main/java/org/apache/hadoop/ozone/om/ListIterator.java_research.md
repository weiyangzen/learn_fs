# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ListIterator.java

## Purpose
`ListIterator` provides common listing machinery for merging sorted entries from RocksDB tables and unflushed table cache. It is used where OM must expose a lexicographically ordered view of resources while respecting cache entries that may create, update, or delete keys not yet flushed to RocksDB.

## Important APIs, types, and functions
The public container class defines `ClosableIterator`, `HeapEntry`, `DbTableIter`, `CacheIter`, and `MinHeapIterator`. `HeapEntry` stores the originating iterator id, table name, key, and value, and compares first by key and then iterator id. `DbTableIter` wraps a `TableIterator<String, KeyValue<String, Value>>` for persisted DB entries. `CacheIter` snapshots matching cache entries into a `TreeMap`. `MinHeapIterator` composes cache and DB iterators for one or more tables and emits globally sorted `HeapEntry` values using a priority queue.

## Control flow
`DbTableIter` opens a table iterator at a prefix and optionally seeks to `startKey` only when `startKey` is lexicographically after the prefix. Its `getNextKey` skips DB keys that exist in cache, which lets cache entries shadow persisted values, including tombstones. IOExceptions from `hasNext` are surfaced as `UncheckedIOException` and converted back in the `MinHeapIterator` constructor.

`CacheIter` consumes the provided table cache iterator immediately into a sorted local map. It includes keys that start with `prefixKey` and, when `startKey` is nonblank, compare at or after `startKey`. Values implementing `CopyObject` are copied before storing to avoid later mutation. Only non-null cache values are emitted; null values still remain in the map so `doesKeyExistInCache` can suppress stale DB entries.

`MinHeapIterator` acquires the OM bucket read lock while building all cache and DB iterators. For each table it adds a `CacheIter`, then a `DbTableIter` whose cache-existence predicate points to that cache iterator. After releasing the lock, it seeds a priority queue with the first entry from each iterator. Each `next` removes the smallest entry and advances only the iterator that produced it.

## State and persistence behavior
The class does not persist data. It reads table cache and RocksDB table iterators and stores a temporary sorted cache snapshot plus live DB iterator handles. Cache tombstones affect output by suppressing DB entries with the same key. `close` must be called on `MinHeapIterator` or `DbTableIter` to release underlying table iterators.

## Dependencies and integration points
It depends on `OMMetadataManager` for bucket locks and table access, `Table` and `TableIterator` from the HDDS DB abstraction, cache key/value types, `BucketLayout` to choose the key table, and `IOUtils.closeQuietly` for iterator cleanup. The default `MinHeapIterator` constructor merges directory and key tables for FSO-style listing, while the varargs constructor can merge arbitrary tables.

## Risks and edge cases
Ordering uses iterator id as a tiebreaker after key. This makes output deterministic, but duplicate keys across tables are not automatically deduplicated unless one duplicate is shadowed by that table's cache predicate. `HeapEntry.equals` delegates to `compareTo`, while `hashCode` uses only key, which is acceptable for key-based heap entries but can produce collisions for duplicate keys from different iterators. `CacheIter` materializes all matching cache entries, so very large cache ranges can increase memory use. Null cache values never emit entries but still hide DB keys, which is essential for delete visibility and should not be removed casually.

## Test signals
Tests should exercise cache-created entries, cache-deleted entries suppressing DB rows, start keys before and after prefixes, multi-table sorted merge, duplicate key ordering, close behavior, `CopyObject` values, and exception propagation from DB iterators.
