# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/reconciliation/TestReconcileContainerEventHandler.java

Purpose: This suite verifies eligibility and command dispatch for `ReconcileContainerEventHandler`, which sends reconcile commands to datanodes hosting eligible container replicas.

Important APIs and types: It uses `ReconcileContainerEventHandler`, `ReconciliationEligibilityHandler`, `EligibilityResult`, `Result`, `ContainerManager`, `SCMContext`, `EventPublisher`, `DATANODE_COMMAND`, `CommandForDatanode<ReconcileContainerCommandProto>`, `SCMCommand`, `ContainerInfo`, `ContainerReplica`, RATIS and EC replication configs, and replica/container lifecycle states.

Control flow: Setup mocks a leader SCM context with a fixed term, a container manager, and an event publisher. Tests create containers and replica sets through helpers, call the static eligibility checker, then invoke `onMessage`. In accepted cases, the event handler fires one datanode command per replica; in rejected cases, no event is fired.

State and persistence behavior: There is no persistence. Runtime state includes mocked container metadata, replica sets, SCM leadership/term, and captured published commands. Command payload state includes container ID, command ID, term, target datanode, and peer list.

Dependencies and integration points: The handler integrates SCM event processing, leadership gating, container manager reads, reconciliation eligibility rules, and datanode command publication. It currently supports RATIS THREE-style reconciliation while rejecting EC and RATIS ONE scenarios.

Risks: Peer-selection behavior is noted as subject to change by a TODO. The tests use mocked manager state and do not validate actual datanode reconciliation execution. The parameterized lifecycle and replica-state tests encode which states are currently eligible.

Test signals: Signals include exact eligibility result codes, no command when SCM is not leader or container is ineligible/missing, three commands for eligible three-replica containers, command term equal to leader term, command ID equal to container ID, and peer lists that include all other replica hosts but exclude the target.
