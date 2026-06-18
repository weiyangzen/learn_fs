# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/LRUCacheTest.java

## Purpose

Smoke-tests `LRUCache` construction and usage counters.

## Important APIs, control flow, and dependencies

The test constructs `LRUCache` with capacity, shard bits, strict capacity limit, high-priority pool ratio, and memory allocator, then reads `getUsage` and `getPinnedUsage`.

## State, persistence, risks, and test signals

No DB is opened. Native cache state is allocated and released through try-with-resources. Risks include constructor signature drift and usage counter JNI issues. Signals are nonnegative usage and pinned usage.
