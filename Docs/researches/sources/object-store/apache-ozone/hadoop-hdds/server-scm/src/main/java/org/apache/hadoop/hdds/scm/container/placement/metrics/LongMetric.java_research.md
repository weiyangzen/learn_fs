# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/LongMetric.java

Purpose: mutable `Long` implementation of `DatanodeMetric`.

Important APIs: constructor, comparison helpers, `hasResources`, `get`, `set`, `add`, `subtract`, `compareTo`, `equals`, and `hashCode`.

Control flow and state: stores a boxed `Long` and mutates it directly. `hasResources` requires strictly greater than requested, not greater-than-or-equal.

Dependencies and integration: embedded in `ContainerStat` and `SCMNodeStat`; serialized by Jackson with field visibility.

Risks: not thread-safe; null values can be set and later cause NPEs in comparison/add/subtract. Strict resource comparison may reject exact-fit resources if used for capacity checks. Test signals should cover exact resource boundary, equality/hash behavior, and mutation effects in parent objects.
