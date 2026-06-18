# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerReplicaPendingOps.java

Purpose: in-memory tracker for pending container replica ADD and DELETE operations across the cluster.

Important APIs/types: constructor, `scheduleAddReplica`, `scheduleDeleteReplica`, completion/removal methods, `removeExpiredEntries`, `getPendingOps`, `clear`, `registerSubscriber`, pending op counters by type/replication type, `getContainerSizeScheduled`, and nested `SizeAndTime`.

Control flow and state: uses `ConcurrentHashMap<ContainerID, List<ContainerReplicaOp>>`, striped read/write locks per container, and a global clear lock. Scheduling removes duplicate same-type target/index ops before adding a new one, increments counters, and tracks pending ADD bytes per target datanode. Completion removes matching ops, decrements counters, releases scheduled size, and notifies subscribers after locks are released. Expiration removes ADD ops but leaves DELETE ops for resending, while still notifying and updating timeout metrics.

Dependencies and integration: used by ReplicationManager, report handlers, block manager setup, and MoveManager callbacks. Tests in `TestReplicationManager` and balancer move tests exercise pending-op behavior.

Risks: `rmConf` may be null, but `releaseScheduledContainerSize` calls `rmConf.getEventTimeout()` on ADD expiration; null config plus expiring ADD can NPE. `subscribers` is an unsynchronized `ArrayList`. Counter/map consistency depends on all mutation paths using locks. Test signals should include duplicate scheduling, concurrent clear/update, ADD size release, DELETE expiry retention, subscriber callbacks, EC/Ratis counters, and null configuration expiration behavior.
