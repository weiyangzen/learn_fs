# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DeletedBlockLogImpl.java

Purpose: Table-backed implementation of `DeletedBlockLog` coordinating deletion transaction persistence, scan selection, duplicate suppression, ACK handling, and metrics.

Important APIs and types: Implements `DeletedBlockLog` and `EventHandler<DeleteBlockStatus>`. Uses `DeletedBlockLogStateManager`, `SCMDeletedBlockTransactionStatusManager`, `ContainerManager`, `SCMContext`, `SequenceIdGenerator`, and `ScmBlockDeletingServiceMetrics`.

Control flow: `addTransactions` converts container block lists to `DeletedBlocksTransaction`s, batching by Ratis appender queue byte limit, then persists through the status manager. `getTransactions` scans from the last cursor, wraps at table end, skips open/unhealthy or unavailable containers, removes stale transactions for missing/deleted containers, avoids duplicate sends, and returns per-datanode work. `onMessage` commits executed ACKs only on the leader and updates command-status records.

State and persistence behavior: Persistent rows live in the deleted-block transaction table and summary in the stateful config table. In-memory state includes a lock, cursor, command timeout, and per-datanode distribution factor.

Dependencies and integration points: Links block-manager delete requests, SCM HA tables, replication health, datanode command events, command-status reports, layout features, and metrics.

Risks: Cursor wrap and skipped transaction behavior affect fairness. Health checks intentionally delay deletion for unsafe containers. Summary accuracy depends on size metadata and `txSizeMap` population.

Test signals: Cover batching, scan wraparound, open/unhealthy/deleted/missing containers, duplicate suppression, ACK success/failure, non-leader skip, timeout cleanup, and summary updates.
