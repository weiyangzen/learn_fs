# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerHealthState.java

## Purpose
Enumerates SCM container health states used by `ContainerInfo`, ReplicationManager reporting, and metrics. It includes individual states and observed combined states.

## Important APIs, Types, And Functions
Constants include `HEALTHY`, `UNDER_REPLICATED`, `MIS_REPLICATED`, `OVER_REPLICATED`, `MISSING`, `UNHEALTHY`, `EMPTY`, `OPEN_UNHEALTHY`, `QUASI_CLOSED_STUCK`, `OPEN_WITHOUT_PIPELINE`, and combined states such as `UNHEALTHY_UNDER_REPLICATED`. Each has a short value, description, and metric name. `fromValue(short)` maps serialized values to enum constants.

## Control Flow
Static initialization fills a lookup map. Runtime code increments metrics, sets `ContainerInfo` health, and decodes short values from persisted/serialized forms.

## State And Persistence
Enum values are stable serialization identifiers; unknown values decode to `HEALTHY`. Descriptions and metric names feed reports/metrics.

## Dependencies And Integration Points
Integrated by `ReplicationManagerReport`, `ContainerInfo`, and replication handlers referenced in comments.

## Risks And Test Signals
Defaulting unknown values to `HEALTHY` can hide forward-incompatible states. Tests should cover value uniqueness, metric names, round trips, and behavior for unknown values.
