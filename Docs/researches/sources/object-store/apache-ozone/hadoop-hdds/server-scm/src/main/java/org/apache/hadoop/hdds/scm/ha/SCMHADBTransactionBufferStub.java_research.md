# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHADBTransactionBufferStub.java

Purpose: Test and Recon-oriented `SCMHADBTransactionBuffer` implementation that batches table writes without the full production HA transaction-info bookkeeping.

Important APIs and types: Constructors accept no store or a `DBStore`; `addToBuffer`, `removeFromBuffer`, `flushIfNeeded`, `flush`, and `close` implement the useful part of the interface. Transaction and snapshot methods are stubs returning null or doing nothing.

Control flow: Writes acquire the read lock, lazily create either a `DBStore` batch or an atomic RocksDB batch, and enqueue table puts/deletes. `flush` takes the write lock, commits through `DBStore` when present, closes the batch, and resets it.

State and persistence behavior: The only meaningful mutable state is `currentBatchOperation`. With a real `DBStore`, flush persists queued mutations; without one, the in-memory atomic operation is closed without durable commit.

Dependencies and integration points: Used by `SCMHAManagerStub` and Recon/test paths that need the same buffer API as production SCM HA.

Risks and test signals: It deliberately omits latest transaction and snapshot tracking, so tests that exercise snapshot, checkpoint, or term-index behavior must not rely on it. Useful assertions are batched table mutation visibility after `flush` and correct cleanup on `close`.
