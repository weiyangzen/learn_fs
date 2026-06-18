# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerReplicaPendingOpsSubscriber.java

Purpose: callback interface for objects interested in pending replica operation completion or timeout.

Important APIs: `opCompleted(ContainerReplicaOp op, ContainerID containerID, boolean timedOut)`.

Control flow and state: interface only. Implementations receive individual operations after pending ops has removed or observed timeout state.

Dependencies and integration: `ContainerReplicaPendingOps` invokes it; `MoveManager` implements it to progress two-phase balancer moves.

Risks: callback name says completed even when `timedOut` is true, so implementers must inspect the flag. Subscribers are invoked synchronously; slow or throwing subscribers can affect notification flow. Tests should include multiple subscribers, timeout and normal completion, and exception containment expectations.
