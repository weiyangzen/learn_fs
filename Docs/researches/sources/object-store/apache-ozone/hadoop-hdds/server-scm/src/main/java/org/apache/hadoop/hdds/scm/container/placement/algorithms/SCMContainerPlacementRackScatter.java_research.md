# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementRackScatter.java

Purpose: rack-scatter placement policy, used especially for EC, that tries to distribute replicas across as many racks as possible while respecting max replicas per rack and resource constraints.

Important APIs: constructors, `chooseDatanodesInternal`, `chooseNodesFromRacks`, private `chooseNode`, `getRequiredRackCount`, `findRacksWithOnlyExcludedNodes`, `sortRackWithExcludedNodes`, and `getAllRacks`.

Control flow and state: filters available nodes, validates enough candidates, shuffles racks and favored nodes, counts used nodes per rack, removes unavailable racks, chooses required new racks first, then fills remaining nodes while honoring max replicas per rack. It validates final placement and avoids worsening mis-replication relative to initial used nodes.

Dependencies and integration: uses `NetworkTopology`, `SCMCommonPlacementPolicy`, `ContainerPlacementStatus`, and metrics. Tested extensively by `TestSCMContainerPlacementRackScatter` and used as default EC placement.

Risks: constructor accepts `fallback` but does not store/use it. The second fill phase adds used racks to the rack list twice, which may be intentional preference or duplicate risk. `chooseNode` mutates the excluded list passed in. Tests should include all-excluded racks, dead nodes with null rack, favored nodes, EC required rack count, and no-worse mis-replication behavior.
