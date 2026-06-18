# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBMetrics.java

## Purpose
`RDBMetrics` is a singleton Metrics2 source for generic RocksDB table operation and WAL delta-update counters.

## Important APIs and Types
`create` registers or returns the singleton. Counters track key may-exist checks/misses, key gets, get-if-exist checks/misses/gets, WAL update data size, and WAL update sequence count. `unRegister` clears the singleton and unregisters the source.

## Control Flow and State
The metrics system injects `MutableCounterLong` fields annotated with `@Metric`. Increment/get methods update or read counters. Singleton creation and unregistration are synchronized.

## Persistence, Dependencies, and Integration
No persistent state exists. Dependencies include Hadoop Metrics2 annotations and `DefaultMetricsSystem`. `RDBStore` creates it and `RDBTable`/WAL update code increment it.

## Risks and Test Signals
Because it is a global singleton, multiple stores share counters and one store close unregisters the source. Tests should isolate metrics system state and cover singleton reuse, increments, WAL counters, unregister/reset, and interaction with multiple `RDBStore` instances.
