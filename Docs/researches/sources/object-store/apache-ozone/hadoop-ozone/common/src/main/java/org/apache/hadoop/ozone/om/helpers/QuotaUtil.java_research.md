<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/QuotaUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/QuotaUtil.java

## Purpose

`QuotaUtil` calculates logical, replicated, and per-replica sizes for quota accounting across RATIS and erasure-coded replication.

## Important APIs, Types, And Functions

It exposes `getReplicatedSize`, `getSizePerReplica`, and `getDataSize`. RATIS uses replication factor multiplication/division. EC uses data/parity chunk geometry and required-node counts.

## Control Flow, State, And Persistence

The class is stateless. `getReplicatedSize` computes EC full stripes plus parity for a partial first chunk; `getDataSize` estimates the inverse because exact partial stripe layout is not knowable from replicated size alone. Unknown replication types log warnings and return the original size.

## Dependencies And Integration Points

It depends on `ReplicationConfig`, `RatisReplicationConfig`, `ECReplicationConfig`, and HDDS replication type enums. It integrates with volume/bucket quota usage, deleted-key accounting, snapshot size accounting, and quota repair.

## Risks And Test Signals

EC reverse sizing is approximate and partial-stripe math must match container layout expectations. Tests should cover RATIS factors, EC exact stripes, small partial writes, zero size, unknown replication type, and `requiredNodes <= 0` fallback in per-replica calculation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/QuotaUtil.java -->
