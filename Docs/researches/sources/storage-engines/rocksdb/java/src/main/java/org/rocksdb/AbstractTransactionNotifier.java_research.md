# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractTransactionNotifier.java

- **Purpose:** Java callback base for notifications when `Transaction#setSnapshotOnNextOperation()` materializes a snapshot.
- **Important APIs/types/functions:** Extends `RocksCallbackObject`; declares abstract `snapshotCreated(Snapshot newSnapshot)`; private JNI hook `snapshotCreated(long snapshotHandle)` wraps the native handle; `initializeNative()` calls `createNewTransactionNotifier()`; disposal calls `disposeInternalJni`.
- **Control flow:** Native transaction code invokes the private long-handle method, which constructs a `Snapshot` wrapper and calls the subclass callback. Native allocation/disposal is controlled by the callback base and explicit dispose path.
- **State and persistence behavior:** No durable state. The callback transfers observation of a native snapshot handle into Java; snapshot lifetime/ownership semantics depend on the `Snapshot` wrapper and transaction lifecycle.
- **Dependencies:** Depends on `RocksCallbackObject`, `Snapshot`, `Transaction`, and JNI notifier functions.
- **Integration points:** Used by transactional RocksDB Java APIs that defer snapshot creation until the next operation and need to hand the created snapshot to Java callers.
- **Risks:** The disposal comment references comparator/transactions and signals lifecycle sensitivity. Retaining the created `Snapshot` beyond its valid transaction/database lifetime can expose invalid native handles. Callback exceptions are not caught here.
- **Test signals:** Snapshot-on-next-operation callback invocation, correct snapshot handle wrapping, callback disposal after transaction close, and behavior when notifier is closed too early.
