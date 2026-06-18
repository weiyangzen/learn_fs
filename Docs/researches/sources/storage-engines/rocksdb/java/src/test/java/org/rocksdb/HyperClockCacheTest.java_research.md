# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/HyperClockCacheTest.java

## Purpose

Smoke-tests `HyperClockCache` creation and integration as a block cache.

## Important APIs, control flow, and dependencies

The test creates a `HyperClockCache`, installs it in `BlockBasedTableConfig.setBlockCache`, opens a DB with `Options`, writes one key/value pair, and reads cache usage and pinned usage.

## State, persistence, risks, and test signals

A temporary DB is opened but persistence semantics are not deeply inspected. The state under test is cache allocation, table config ownership, and ability to query native usage counters. Risks include constructor parameter mismatch and cache/table-config lifetime bugs. Signals are nonnegative usage counters after DB use.
