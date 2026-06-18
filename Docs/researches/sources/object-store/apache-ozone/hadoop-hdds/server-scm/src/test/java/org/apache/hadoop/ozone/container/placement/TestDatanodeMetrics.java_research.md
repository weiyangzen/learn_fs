# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/ozone/container/placement/TestDatanodeMetrics.java

Purpose: This unit test validates comparison and aggregation behavior for placement metrics represented by `SCMNodeMetric` and `SCMNodeStat`.

Important APIs and types: It constructs `SCMNodeStat` values containing capacity, SCM-used, remaining, committed, free space, and other counters, wraps them in `SCMNodeMetric`, and calls `isEqual`, `add`, and `isGreater`.

Control flow: The test creates an initial stat and verifies its accessors. It creates an equivalent metric and checks equality, adds the original stat to the new metric and checks greater-than comparison, compares against a zero-capacity metric, and verifies that a small used-space difference on large-capacity nodes is ordered correctly.

State and persistence behavior: There is no persistence. State is in-memory metric values and derived comparison weights.

Dependencies and integration points: These metrics are used by SCM placement algorithms to rank datanodes by capacity pressure and space utilization. The test supports the placement behavior covered by `TestContainerPlacement`.

Risks: It covers only a few comparison scenarios and does not exhaust rounding or committed-space effects. A change to comparison semantics may require reinterpreting the final large-capacity assertion.

Test signals: Exact getter values, equality for identical stats, greater-than after addition, safe comparison against zero capacity, and greater-than for 51 used versus 50 used on otherwise identical large nodes.
