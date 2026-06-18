# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/SCMCommonPlacementPolicy.java

Purpose: Shared base class for SCM placement policies, enforcing common healthy-node, space, peer-removal, topology-validation, and repair-selection behavior.

Important APIs and types: Includes `chooseDatanodes`, `chooseDatanodesInternal`, `filterNodesWithSpace`, `hasEnoughSpace`, `getResultSet`, abstract `chooseNode`, `validateContainerPlacement`, `isValidNode`, and replica repair methods. Uses `NodeManager`, `DatanodeInfo`, `NodeStatus`, `NetworkTopology`, `ContainerReplica`, and `SCMException`.

Control flow: Normalizes datanode objects via `NodeManager`, removes excluded/used nodes, validates healthy-node count, filters by metadata/data space, and delegates final selection to subclasses. Placement validation groups replicas by rack/placement group, handles empty topology, computes max replicas per rack, and adjusts for overreplication.

State and persistence behavior: Holds node manager, config, random, and cached simple placement statuses. Reads live node/topology/storage state; persists nothing.

Dependencies and integration points: Base for placement algorithms and Replication Manager validation/repair logic. Peer removal is controlled by `ScmUtils.shouldRemovePeers`.

Risks: `hasEnoughSpace` requires `DatanodeInfo`. Empty or transient topology needs guards. Repair algorithms depend on placement group availability and replica-index grouping.

Test signals: Cover healthy-node shortage, space shortage, deserialized datanode normalization, rack validation, empty topology, peer removal, and copy/remove repair decisions.
