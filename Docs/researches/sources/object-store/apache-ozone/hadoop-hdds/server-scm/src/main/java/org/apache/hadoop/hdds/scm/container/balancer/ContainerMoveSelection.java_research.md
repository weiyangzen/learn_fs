# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerMoveSelection.java

Purpose: mutable pair describing a selected container and its target datanode for a balancer move.

Important APIs: constructor, getters/setters for `DatanodeDetails targetNode` and `ContainerID containerID`, plus `equals`/`hashCode`.

Control flow and state: a simple DTO with mutable fields and no synchronization. It does not persist anything and is expected to be short lived during target selection.

Dependencies and integration: returned by `FindTargetStrategy.findTargetForContainerMove()` implementations and consumed by the container balancer task before invoking `MoveManager`.

Risks: `equals()` compares `targetNode` and `containerID` using reference identity (`!=` and `==`) while `hashCode()` uses `Objects.hash`, which delegates to value equality. This can violate the equals/hashCode contract if logically equal but non-identical objects are used. Mutability also makes it unsafe as a map key after mutation. Test signals should include equality contract tests if this object is ever stored in sets or maps.
