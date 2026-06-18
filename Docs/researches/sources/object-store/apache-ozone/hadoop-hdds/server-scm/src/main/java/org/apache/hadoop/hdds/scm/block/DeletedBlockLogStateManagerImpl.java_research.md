# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DeletedBlockLogStateManagerImpl.java

Purpose: Persists deleted-block transactions and summary data via SCM's HA transaction buffer while hiding unflushed removals from scans.

Important APIs and types: Uses deleted transaction table, stateful config table, `ContainerManager`, `SCMHADBTransactionBuffer`, and transient `deletingTxIDs`. Provides builder wrapping with `DeletedBlockLogStateManagerInvoker`.

Control flow: The read-only iterator skips transactions in `deletingTxIDs`. Adds buffer transaction rows, update latest delete transaction ID per container, and optionally write summary. Removes mark IDs in `deletingTxIDs`, enqueue table removals, and optionally write summary. `onFlush` clears deletion marks.

State and persistence behavior: Persistent mutations are staged in the HA transaction buffer. `deletingTxIDs` is transient protection against selecting rows already queued for removal.

Dependencies and integration points: Integrates with SCM Ratis proxying, metadata tables, transaction buffering, and container transaction ID tracking.

Risks: Missing `onFlush` could hide rows indefinitely. Reinitialization asserts there are no pending deleting IDs. Iterator is intentionally read-only and lacks `seekToLast`.

Test signals: Cover iterator skipping, add/remove buffering, summary writes, container update calls, flush clearing, and builder proxy creation.
