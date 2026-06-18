<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/RawDB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/RawDB.java

## Purpose

`RawDB` is a thin `DBHandle` wrapper for schema-v3 per-disk datanode stores. Its key behavior is that `close()` intentionally does nothing because individual container operations must not close a shared per-disk RocksDB handle. The complete 40-line file was read.

## Important APIs, Types, and Functions

The class extends `DBHandle`, has a constructor accepting `DatanodeStore` and DB path, and overrides `close()`.

## Control Flow

There is no operational flow beyond construction and no-op close.

## State and Persistence Behavior

It stores the underlying `DatanodeStore` and path via `DBHandle`. Persistence is managed by the store and by `DatanodeStoreCache`, which eventually calls `store.stop()`.

## Dependencies and Integration Points

It integrates with `DatanodeStoreCache` and schema-v3 block code that expects a `DBHandle` but must not own the shared store lifecycle.

## Risks and Edge Cases

Generic code that assumes `DBHandle.close()` releases resources will not release schema-v3 stores when passed `RawDB`. That is intentional but must remain documented.

## Test Signals

Tests should verify close is no-op, cache removal/shutdown stops the underlying store, and callers do not rely on try-with-resources to close schema-v3 shared DBs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/RawDB.java -->
