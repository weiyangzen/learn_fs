# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerHealthResult.java

Purpose: result hierarchy representing container replication health and any commands generated while checking it.

Important APIs/types: base `ContainerHealthResult`, `HealthyResult`, `UnHealthyResult`, `UnderReplicatedHealthResult`, `MisReplicatedHealthResult`, `OverReplicatedHealthResult`, and enum `HealthState`.

Control flow and state: base stores container info, health state, and mutable command list. Under-replicated results track remaining redundancy, out-of-service weighting, pending sufficiency, unrecoverable/missing/offline-index flags, healthy replica presence, vulnerable unhealthy replicas, and requeue count. Mis-replication subclasses under-replication with weighted redundancy 6. Over-replication tracks excess redundancy, pending correction, mismatched replicas, and safe over-replication.

Dependencies and integration: produced by replication health handlers and consumed by ReplicationManager queues, balancer selection, deleted block log, and tests.

Risks: mutable command list is exposed directly; requeue count mutates priority semantics. Mis-replication inheriting under-replication behavior requires careful queue tests. Test signals should cover weighted redundancy ordering, pending-corrected flags, missing/unrecoverable flags, over-replicated safety, and balancer rejection/allowance decisions.
