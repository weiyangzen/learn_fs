<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/DatanodeStoreCache.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/DatanodeStoreCache.java

## Purpose

`DatanodeStoreCache` is a singleton cache for schema-v3 per-disk `DatanodeStore` handles. Unlike `ContainerCache`, schema v3 shares one RocksDB instance per disk, so raw DB close is centralized at cache shutdown or explicit removal. The complete 125-line file was read.

## Important APIs, Types, and Functions

Public methods include `getInstance()`, testing `setMiniClusterMode`, `addDB`, `getDB`, `removeDB`, `shutdownCache`, and `size`. The map key is the container DB absolute path and values are `RawDB`.

## Control Flow

`getDB` first checks a concurrent map, then synchronizes on the cache object for double-checked creation. It opens a `DatanodeStoreSchemaThreeImpl` in read-write mode, wraps it in `RawDB`, and stores it. `removeDB` removes and stops the store if present. `shutdownCache` either skips clearing in mini-cluster mode, logging remaining keys, or stops every store and clears the map.

## State and Persistence Behavior

Runtime state is `datanodeStoreMap` and `miniClusterMode`. Persistent state is the per-disk RocksDB store; the cache manages handle lifetime and does not alter metadata by itself.

## Dependencies and Integration Points

It depends on `DatanodeStoreSchemaThreeImpl`, `RawDB`, `ConfigurationSource`, and schema-v3 block/metadata code that calls `BlockUtils.addDB` or store cache accessors.

## Risks and Edge Cases

Mini-cluster mode intentionally leaks cache entries across shutdown to support test cluster lifetimes, which can surprise tests that expect full cleanup. Creation is synchronized globally rather than per path. `addDB` uses `putIfAbsent` and does not close or reject a supplied duplicate handle.

## Test Signals

Tests should cover double-checked creation, remove/stop behavior, shutdown behavior with and without mini-cluster mode, duplicate `addDB`, IOException wrapping during open, and cache size tracking.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/DatanodeStoreCache.java -->
