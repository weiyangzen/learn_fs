## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStoreSchemaTwoImpl.java

Purpose: Opens and exposes schema-two datanode stores with incremental chunk-list support and long-keyed delete transactions.

Important APIs and functions: The constructor builds `DatanodeStoreWithIncrementalChunkList` using `DatanodeSchemaTwoDBDefinition`, then retrieves the delete transactions table. `getDeleteTransactionTable()` returns `Table<Long, DeletedBlocksTransaction>`.

Control flow and state: The implementation carries only the delete transaction table field beyond inherited table state. Block data, metadata, finalize, and last-chunk table setup is inherited.

Persistence and dependencies: Persists delete transactions in the `delete_txns` CF using `LongCodec` keys and protobuf values. Inherits block/metadata persistence and incremental chunk handling.

Risks: Because delete transactions are not container-prefixed, schema-two DBs must remain one DB per container. Table status is not explicitly checked here after retrieval, so DBDefinition/store build correctness is important. Delete task casts this store through `DeleteTransactionStore<Long>`.

Test signals: Store construction, delete transaction put/get/delete/range through block deletion, incremental chunk list writes, finalized block table use, read-only open, and schema-two block deletion flow.
