# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/SCMNodeMetric.java

Purpose: comparable metric wrapper around `SCMNodeStat` for placement and pipeline capacity comparisons.

Important APIs: constructors, `isGreater`, `isLess`, `isEqual`, `hasResources`, `get`, `set`, `add`, `subtract`, `compareTo`, equality/hash, and `toString`.

Control flow and state: compares nodes primarily by used/capacity utilization with epsilon tolerance, then by raw used bytes. Zero capacity denominators are replaced by one in `isGreater`/`isLess`, but not in `isEqual`.

Dependencies and integration: returned by `NodeManager.getNodeStat`; used by capacity placement and pipeline choose policy. Tested through node and pipeline tests.

Risks: `hasResources` always returns false, so it should not be used as a real resource check. `isEqual` can divide by zero and produce NaN behavior for zero-capacity stats. `compareTo` equality by utilization may be inconsistent with `equals` by full stat. Test signals should cover zero capacity, sorted collection behavior, and comparator ties.
