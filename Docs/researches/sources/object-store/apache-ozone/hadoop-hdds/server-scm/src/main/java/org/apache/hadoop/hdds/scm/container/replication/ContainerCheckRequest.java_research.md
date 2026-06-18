# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerCheckRequest.java

Purpose: immutable request wrapper for container health checks in ReplicationManager.

Important APIs: getters, nested `Builder` setters, and `build`.

Control flow and state: constructor wraps replica set and pending ops list with unmodifiable views. It stores container info, maintenance redundancy, report, replication queue, and read-only flag.

Dependencies and integration: passed to replication health check handlers; combines `ContainerInfo`, `ContainerReplica`, `ContainerReplicaOp`, `ReplicationManagerReport`, and `ReplicationQueue`.

Risks: builder does not validate required fields; null `containerReplicas` or `pendingOps` will cause NPE in construction, while null report/queue may fail later. Unmodifiable wrappers are shallow and reflect mutations to the original collection if the caller keeps it. Tests should cover builder completeness, read-only behavior in handlers, and immutability expectations.
