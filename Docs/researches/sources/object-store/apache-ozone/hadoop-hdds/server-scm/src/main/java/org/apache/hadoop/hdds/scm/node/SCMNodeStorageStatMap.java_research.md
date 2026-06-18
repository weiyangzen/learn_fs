# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/SCMNodeStorageStatMap.java

## Purpose
`SCMNodeStorageStatMap` maintains storage-location reports per datanode and classifies node reports by utilization and failed-volume conditions. It implements `SCMNodeStorageStatMXBean` for storage JMX views.

## Important APIs, Types, And Functions
The constructor reads warning and critical utilization thresholds. `isKnownDatanode`, `insertNewDatanode`, `updateDatanodeMap`, and `removeDatanode` manage the `UUID -> Set<StorageLocationReport>` map. `processNodeReport` converts protobuf storage reports, tracks failed and critically full volumes, updates the map, logs threshold warnings, and returns `StorageReportResult`. JMX methods aggregate capacity, remaining, and used space per node or cluster-wide. `getDatanodeList` filters datanodes by `UtilizationThreshold`, and `getScmUsedratio` truncates utilization to four decimal places.

## Control Flow
Processing a node report iterates each storage report, converts it to a `StorageLocationReport`, adds failed volumes to one set, adds critically utilized nonfailed volumes to another, and accumulates total capacity, remaining, and SCM-used bytes. It inserts or replaces the datanode's report set, then prioritizes status as datanode out-of-space if aggregate utilization is critical. Otherwise it logs warning threshold crossings and returns one of all-well, storage-out-of-space, failed-storage, or combined failure statuses based on the volume sets.

## State And Persistence Behavior
State is a `ConcurrentHashMap<UUID, Set<StorageLocationReport>>`, with synchronized blocks around insert/update/remove despite the concurrent map. There is no durable persistence; the map is rebuilt from datanode reports. Returned sets are direct map values, not defensive copies, so callers can observe and potentially mutate internal state if they retain references.

## Dependencies And Integration Points
The class depends on Ozone configuration keys for thresholds, protobuf `NodeReportProto` and `StorageReportProto`, `StorageLocationReport`, and `SCMException` result codes. It is an older storage-report processing and JMX component adjacent to the newer `DatanodeInfo` storage report handling in `SCMNodeManager`.

## Risks And Edge Cases
`getCapacity`, `getRemainingSpace`, and `getUsedSpace` assume the datanode ID is present; unknown IDs cause null iteration failures rather than clean exceptions. `getScmUsedratio` divides by capacity, so zero-capacity reports are risky. `putIfAbsent` is redundant inside synchronization. The local variable `storagReportSet` is misspelled but harmless. Directly returning internal volume sets can corrupt future aggregates.

## Test Signals
Tests should cover first report insert, report update, duplicate and missing datanode exceptions, warning/critical thresholds, failed and full volume combinations, zero/invalid capacity handling, aggregate totals, datanode list filtering by utilization threshold, and mutation safety of returned storage-volume sets.
