# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DatanodeUsageInfo.java

Purpose: `DatanodeUsageInfo` bundles `DatanodeDetails` with capacity, usage, container count, pipeline count, reserved bytes, and optional filesystem-level usage for client/admin views and sorting.

Important APIs and types: Important methods are `calculateUtilization`, `getMostUtilized`, getters/setters for datanode/stat/count fields, `setFilesystemUsage`, `equals`, `hashCode`, and `toProto(int clientVersion)`. It wraps `SCMNodeStat` and emits `HddsProtos.DatanodeUsageInfoProto`.

Control flow: Utilization is calculated as `(capacity - remaining + plusSize) / capacity`, returning zero for zero capacity and intentionally not using SCM-used bytes. The comparator delegates to utilization and treats equal datanode identity as equal. `toProtoBuilder` conditionally writes datanode details and SCM stats, then always writes counts/reserved and optional filesystem usage.

State and persistence behavior: The object is an in-memory DTO. Defaults for container and pipeline counts are `-1`, indicating unknown. Filesystem usage is present only after `setFilesystemUsage`.

Dependencies and integration points: `NodeManager.getMostOrLeastUsedDatanodes` and usage APIs expose instances of this class to admin/client callers. It depends on `SCMNodeStat` counters and datanode protobuf conversion.

Risks: Equality is based only on datanode details, not current usage, so collections can treat two different usage snapshots for the same datanode as duplicates. The utilization comparator can produce equal order for distinct nodes with the same utilization. Proto output uses SCM-used for the `used` field even though utilization uses capacity-minus-remaining, so callers must understand the distinction.

Test signals: Tests should cover zero-capacity utilization, plus-size utilization, comparator ordering, proto field population with and without optional filesystem usage, unknown count defaults, and equality/hash behavior.
