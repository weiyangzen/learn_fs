<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ReadConsistency.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ReadConsistency.java

## Purpose

`ReadConsistency` defines read-consistency modes for OM client requests, including whether a request must be linearizable and whether follower reads are allowed.

## Important APIs, Types, And Functions

Enum values are `DEFAULT`, `LOCAL_LEASE`, `LINEARIZABLE_LEADER_ONLY`, and `LINEARIZABLE_ALLOW_FOLLOWER`. Methods include `isLinearizable`, `allowFollowerRead`, `toProto`, `toReadConsistencyHint`, and static `fromProto`.

## Control Flow, State, And Persistence

The enum is immutable. It caches protobuf `ReadConsistencyHint` instances and maps between Java and protobuf enums. These hints travel with requests; they are not persisted metadata.

## Dependencies And Integration Points

It depends on `ReadConsistencyProto` and `ReadConsistencyHint` protobufs. It is used by `Hadoop3OmTransport` follower-read failover configuration and by request builders/translators that need to select leader-only, follower-allowed, or local-lease reads.

## Risks And Test Signals

`valueOf` use in configuration paths is case-sensitive and will fail for invalid strings. Tests should cover all enum-protobuf round trips, hint object mapping, follower-read routing decisions, and invalid config values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ReadConsistency.java -->
