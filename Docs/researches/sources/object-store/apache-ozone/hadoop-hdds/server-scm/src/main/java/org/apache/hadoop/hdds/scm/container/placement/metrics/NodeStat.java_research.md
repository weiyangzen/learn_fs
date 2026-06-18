# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/NodeStat.java

Purpose: package-private interface describing SCM node capacity and usage statistics.

Important APIs: getters for capacity, SCM used, remaining, committed, free space to spare, and reserved; test-visible `set`; `add`; `subtract`.

Control flow and state: interface only. Implementations decide validation and mutability; `SCMNodeStat` is the concrete class in this subset.

Dependencies and integration: used by `SCMNodeStat` and `SCMNodeMetric` to support node manager statistics and placement comparisons.

Risks: package-private visibility limits external contract enforcement. Add/subtract may allow negative derived values unless implementations guard. Test signals should focus on concrete `SCMNodeStat` arithmetic and equality.
