# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/ContainerPlacementPolicyFactory.java

Purpose: factory that instantiates configured container placement policy implementations for replicated and EC containers.

Important APIs: `getPolicy`, `getECPolicy`, and private `getPolicyInternal`. Defaults are `SCMContainerPlacementRackAware` for replicated placement and `SCMContainerPlacementRackScatter` for EC placement.

Control flow and state: reads configured class from `ConfigurationSource`, finds a constructor `(NodeManager, ConfigurationSource, NetworkTopology, boolean, SCMContainerPlacementMetrics)`, and invokes it reflectively. No persistence or static mutable state beyond constants.

Dependencies and integration: uses `ScmConfigKeys` placement keys, `PlacementPolicy`, `NodeManager`, `NetworkTopology`, and placement metrics. Used by SCM and balancer mock/test setup. Covered by `TestContainerPlacementFactory`.

Risks: constructor error message omits the metrics parameter in text; instantiation exceptions are wrapped in `RuntimeException`, not `SCMException`, which can surprise callers. Tests should cover bad class, missing constructor, default replicated policy, default EC policy, and custom policy creation.
