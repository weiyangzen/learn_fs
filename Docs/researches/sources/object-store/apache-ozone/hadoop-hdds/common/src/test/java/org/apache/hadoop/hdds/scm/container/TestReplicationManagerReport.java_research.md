# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestReplicationManagerReport.java

## Purpose
Tests `ReplicationManagerReport` metric counting, sample collection, JSON rendering, protobuf serialization, duplicate protection, and tolerance of unknown metrics.

## Important APIs, types, and functions
- Uses `ReplicationManagerReport`, `ContainerHealthState`, `ContainerInfo`, `ContainerID`, and `HddsProtos.LifeCycleState`.
- Exercises `increment`, `incrementAndSample`, `setComplete`, `setTimestamp`, `setStat`, `setSample`, `toProtobuf`, and `fromProtobuf`.
- Uses Jackson `ObjectMapper` through `JsonUtils` for JSON validation.

## Control flow
Tests increment lifecycle and health counters, attach mocked container IDs as samples, render JSON, validate sample-limit configuration, serialize random stats and samples to protobuf, deserialize back, and assert duplicate stat/sample setters throw.

## State and persistence behavior
Report fields model persisted or transmitted SCM health report state. Timestamp, sample limit, stats map, and sample lists are mutated in memory and round-tripped through protobuf.

## Dependencies and integration points
The report integrates SCM replication manager metrics with JSON APIs and HDDS protobufs used for persistence or transmission.

## Risks and test signals
Risks include duplicate metric writes, unknown metric incompatibility, sample over-collection, and JSON/protobuf drift. The suite signals report stability for operational metrics and upgrade tolerance.
