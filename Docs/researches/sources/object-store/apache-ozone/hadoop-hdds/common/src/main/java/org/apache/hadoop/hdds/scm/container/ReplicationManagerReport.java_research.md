# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ReplicationManagerReport.java

## Purpose
Aggregates ReplicationManager run statistics: lifecycle counts, health-state counts, bounded samples of affected container IDs, and completion timestamp.

## Important APIs, Types, And Functions
`increment`, `incrementAndSample`, `getStats`, `getSamples`, `getStat`, `getSample`, `setComplete`, `toProtobuf`, and `fromProtobuf` are key. Stats are keyed by lifecycle-state strings and `ContainerHealthState.name()`, backed by `LongAdder`. Samples are stored in a concurrent map of synchronized lists.

## Control Flow
A manager run creates a report, increments lifecycle and health counters while scanning containers, samples up to `sampleLimit`, then calls `setComplete`. Reports can be serialized to `ReplicationManagerReportProto` and reconstructed, ignoring unknown stat keys.

## State And Persistence
The report is mutable and transient during a scan. Serialized protobufs can be persisted or served through APIs. `containerHealthState` tracks the most recent sampled health state and can be reset.

## Dependencies And Integration Points
Depends on HddsProtos and `ContainerID`/`ContainerInfo`/`ContainerHealthState`. Integrated by ReplicationManager metrics, Recon, and admin diagnostics.

## Risks And Test Signals
`containerHealthState` represents last incremented health state, not aggregate status. Unknown protobuf stats are ignored. Tests should cover concurrent increments, sample limits, serialization round trip, unknown-stat handling, and timestamp completion.
