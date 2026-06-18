# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/PlacementPolicy.java

Purpose: SCM contract for datanode selection and container replica placement validation/repair.

Important APIs and types: Defines overloaded `chooseDatanodes`, `validateContainerPlacement`, `replicasToCopyToFixMisreplication`, and `replicasToRemoveToFixOverreplication`.

Control flow: The default overload forwards with an empty used-node list. Implementations choose nodes, validate placement status, and recommend copy/delete actions to repair misreplication or overreplication.

State and persistence behavior: Stateless interface; concrete policies consult live node, topology, and capacity state.

Dependencies and integration points: Used by SCM allocation and Replication Manager repair flows through `ContainerPlacementStatus` and `ContainerReplica`.

Risks: The default overload cannot distinguish absent used nodes from intentionally empty used nodes; `SCMCommonPlacementPolicy` adds sentinel handling for this.

Test signals: Implementation coverage should include exclusions, used/favored nodes, capacity failures, rack validation, and repair choices.
