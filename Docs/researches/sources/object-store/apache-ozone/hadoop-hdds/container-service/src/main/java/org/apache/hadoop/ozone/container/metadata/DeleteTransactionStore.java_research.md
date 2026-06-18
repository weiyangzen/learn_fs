## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DeleteTransactionStore.java

Purpose: Small schema-neutral interface for stores that expose a delete transaction table.

Important APIs and functions: `getDeleteTransactionTable()` returns `Table<TXN_KEY, DeletedBlocksTransaction>`, where the key type is schema-specific: `Long` for schema two and `String` for schema three.

Control flow and state: The interface is stateless and used for casts by block deletion code after schema dispatch.

Persistence and dependencies: It abstracts the RocksDB delete transaction column family that stores SCM delete transactions until chunks and block metadata are removed.

Risks: Callers must choose the correct generic key type for the schema. A wrong cast would fail at runtime or delete the wrong transaction key. Schema one does not implement this interface because it uses deleting block key prefixes instead of transaction tables.

Test signals: Compile-time coverage for schema-two and schema-three implementations, block deletion casts by schema, transaction table CRUD, and unsupported schema-one path avoiding this interface.
