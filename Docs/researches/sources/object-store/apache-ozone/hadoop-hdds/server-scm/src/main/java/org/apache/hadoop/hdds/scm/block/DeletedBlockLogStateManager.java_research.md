# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DeletedBlockLogStateManager.java

Purpose: HA-replicated state-management interface for deleted-block transaction table mutations.

Important APIs and types: Extends `SCMHandler`, returns `RequestType.BLOCK`, and marks add/remove methods with `@Replicate`. Exposes read-only iteration, flush handling, and reinitialization.

Control flow: Add/remove calls are routed through SCM HA proxy machinery. Overloads can persist `DeletedBlocksTransactionSummary` with transaction changes. Deprecated retry-count methods are retained as no-op replicated methods.

State and persistence behavior: Implementations write deleted-block transaction rows and optional summary bytes to SCM metadata.

Dependencies and integration points: Connects `DeletedBlockLogImpl` and transaction status management to Ratis replication and SCM tables.

Risks: Mutations must go through replicated methods to preserve HA consistency. Deprecated retry methods should not be used for durable retry state.

Test signals: Verify replicated add/remove, summary persistence, iterator behavior, flush cleanup, and reinitialize.
