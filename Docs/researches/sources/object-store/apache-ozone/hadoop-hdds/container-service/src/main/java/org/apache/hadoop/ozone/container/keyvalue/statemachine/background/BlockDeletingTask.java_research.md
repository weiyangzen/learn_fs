## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/statemachine/background/BlockDeletingTask.java

Purpose: Implements the background task that physically deletes blocks/chunks for key-value containers and reconciles delete metadata, statistics, checksums, and pending-delete counters across datanode DB schemas.

Important APIs and functions: `call()` repeatedly invokes `handleDeleteTask()` until the assigned block budget is consumed or no progress is made. `deleteViaSchema1()` scans deleting block keys in the block table. `deleteViaSchema2()` and `deleteViaSchema3()` read delete transaction tables and delegate to `deleteViaTransactionStore()`. `deleteTransactions()` performs chunk deletion through the container `Handler`, handles duplicate local IDs, and tracks released/processed bytes.

Control flow and state: The task locks the live container through `ContainerSet.getContainerWithWriteLock()`, refreshes `containerData` from the locked container, opens the DB, branches by schema, deletes files first, records deleted blocks in the checksum tree, then batches DB metadata removal and counter updates. Schema v3 uses container-prefixed transaction keys; schema v2 uses long transaction IDs.

Persistence and dependencies: It persists changes to block tables, last-chunk tables, delete transaction tables, DB counters, in-memory `KeyValueContainerData` statistics, volume used-space counters, and `ContainerChecksumTreeManager`. It depends on `BlockDeletingService`, `OzoneContainer`, container handlers, `BlockUtils`, `KeyValueContainerUtil`, and RocksDB `BatchOperation`.

Risks: File deletion and DB mutation are not one atomic filesystem/DB transaction. A failed chunk delete can leave delete transactions pending. Processed-byte and released-byte accounting diverge for missing/unreferenced blocks. The max lock-hold time can leave partial transaction batches for future runs. Schema v1 relies on key prefix filtering in a shared default table. Marking a container empty depends on `container.hasBlocks()` after deletes.

Test signals: Cover all three schemas, empty/missing data directory, container lock retry exhaustion, missing block metadata, unreferenced files, duplicate local IDs across transactions, DB batch failure after file deletion, checksum tree updates before transaction removal, max lock-hold cutoff, counter/volume decrements, and no-progress loop break.
