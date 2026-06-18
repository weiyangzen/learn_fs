## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/NoOpsContainerReplicaPendingOps.java

Purpose: no-op `ContainerReplicaPendingOps` implementation used by Recon's local replication manager so health checks can run without issuing or tracking replication commands.

Important APIs/types/functions: overrides `getPendingOps`, schedule add/delete, complete add/delete, and `getPendingOpCount`.

Control flow: all query methods return empty/zero/false and all scheduling methods do nothing. Constructor delegates clock/config to the superclass.

State and persistence: no stored operations, no DB writes. It integrates with `ReconReplicationManager` superclass construction and SCM replication health code.

Risks: correctness depends on SCM health-state determination continuing to ignore pending operations for read-only analysis. If upstream SCM changes health logic to depend on pending operations, Recon could report different health states. Tests should compare health classifications with and without pending ops and verify no command scheduling side effects.
