# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/DatanodeMetric.java

Purpose: generic metric interface for comparing datanode metrics and checking resource availability.

Important APIs: comparison helpers `isGreater`, `isLess`, `isEqual`; `hasResources`; `get`; `set`; `add`; `subtract`.

Control flow and state: interface only; implementations define mutability and comparison semantics.

Dependencies and integration: implemented by `LongMetric` and `SCMNodeMetric`; used by placement and pipeline selection to compare capacity utilization.

Risks: `hasResources` has implementation-specific meaning and can be misleading where implementations return placeholders. Tests should be implementation-specific and verify comparator consistency with equals/hashCode where values are used in sorted collections.
