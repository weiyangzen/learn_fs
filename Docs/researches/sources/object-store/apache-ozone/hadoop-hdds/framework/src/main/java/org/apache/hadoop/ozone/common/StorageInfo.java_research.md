# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/StorageInfo.java

## Purpose

`StorageInfo` owns the common properties stored in an Ozone storage VERSION file and validates them when read. The complete 211-line source was read for this report.

## Important APIs, Types, and Functions

Properties include `nodeType`, `clusterID`, `cTime`, `layoutVersion`, and `firstUpgradeActionLayoutVersion`. APIs include constructors from values or file, getters/setters/unsetters, `writeTo`, and static `newClusterID`.

## Control Flow

The value constructor populates required properties. The file constructor reads properties and verifies node type, cluster ID, creation time, and layout version. Missing layout version is defaulted to `0` with a warning. `newClusterID` prefixes a UUID with `OzoneConsts.CLUSTER_ID_PREFIX`.

## State and Persistence Behavior

State is held in a `Properties` object and persisted via `IOUtils.writePropertiesToFile`. Reads use `IOUtils.readPropertiesFromFile`. The layout version and first-upgrade-action layout version coordinate upgrade finalization state.

## Dependencies and Integration Points

It depends on `NodeType`, `IOUtils`, `OzoneConsts`, and `InconsistentStorageStateException`. `Storage` uses it for VERSION handling; upgrade finalizers update layout version through `Storage`.

## Risks and Edge Cases

`getLayoutVersion` returns `0` if absent, but verification mutates missing layout into `0`. Parsing invalid numeric fields throws. `Properties` is mutable and exposed indirectly through generic property methods. File writes must be atomic enough for storage semantics, which is delegated to `IOUtils`.

## Test Signals

Tests should cover reading valid/invalid VERSION files, node type mismatch, missing/empty cluster ID, missing layout version defaulting, first-upgrade-action property, cluster ID format, and write/read round trips.
