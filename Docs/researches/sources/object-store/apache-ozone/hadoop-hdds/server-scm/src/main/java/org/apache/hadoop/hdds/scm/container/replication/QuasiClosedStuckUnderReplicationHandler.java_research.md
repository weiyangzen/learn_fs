# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/QuasiClosedStuckUnderReplicationHandler.java

Purpose: `QuasiClosedStuckUnderReplicationHandler` creates additional replicas for quasi-closed stuck Ratis containers, preserving each origin according to the origin-aware counts from `QuasiClosedStuckReplicaCount`.

Important APIs and behavior: `processAndSendCommands` skips empty containers because `EmptyContainerHandler` will delete them, suppresses work while pending adds exist, builds a count object with configured best/other origin copy targets, finds under-replicated origins, chooses targets per origin, and sends push replication commands with replica index `0`.

Control flow: for each mis-replicated origin, it asks placement for `replicaDelta` targets using current replicas plus a mutable pending-op list. After each successful command it appends a synthetic pending ADD to the mutable list so later origins do not choose the same target. Source datanodes are all replicas in the origin source set. If target selection or command sending fails, it records the first exception, continues where possible, increments partial metrics when not all required replicas were scheduled, and rethrows or raises `InsufficientDatanodesException`.

State and persistence: local state is limited to counters and mutable pending ops for one processing call. Durable command state is scheduled by `ReplicationManager.sendThrottledReplicationCommand`.

Dependencies and integration: it depends on Ratis placement policy, SCM container size config, `ReplicationManagerUtil`, `ReplicationManager`, metrics, and `QuasiClosedStuckReplicaCount`. `ReplicationManager` routes Ratis under-replicated results to this handler when the quasi-closed stuck health check says the container needs special handling.

Risks: source lists are origin-specific but not filtered by node health in this handler; the count object includes all replicas passed by the caller, so routing must provide appropriate replica sets and command throttling must handle overloaded sources. Pending-add suppression at the top means only one batch is scheduled at a time, which avoids overfill but can slow recovery across many origins.

Test signals: `TestQuasiClosedStuckUnderReplicationHandler` covers empty-container skipping, pending-add suppression, target selection with mutable pending ops, partial failure metrics, insufficient datanodes, and best/other origin configuration.
