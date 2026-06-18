# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestDatanodeStoreCache.java

Purpose: This test verifies basic operations of `DatanodeStoreCache`, a singleton cache for raw datanode DB stores used by schema-v3/shared DB paths.

Important APIs and types: The test uses `DatanodeStoreCache.getInstance`, `addDB`, `getDB`, `removeDB`, `shutdownCache`, `size`, `RawDB`, and `DatanodeStoreSchemaThreeImpl`.

Control flow: It creates two temporary DB directories, constructs two schema-v3 stores, adds both to the cache, verifies duplicate add does not increase size, gets one path back and checks it references the same underlying store object, removes one DB, tolerates removing a non-existent DB, and finally shuts down the cache.

State and persistence behavior: Persistent state is two created schema-v3 DB directories. Runtime cache state is the key-to-`RawDB` map. The test checks object identity with `assertSame` to ensure cached stores are reused rather than reopened.

Dependencies and integration points: It uses `OzoneConfiguration`, temp directories, schema-v3 metadata store implementation, and the raw DB wrapper used by container metadata code. It complements the more elaborate `ContainerCache` tests for per-container DB handles.

Risks: Because the cache is singleton state, `shutdownCache` is important for isolation. The test covers add/get/remove/shutdown but not concurrent access or closed-store recovery.

Test signals: Cache sizes 2, 2 after duplicate add, 1 after remove, and 0 after shutdown, plus same-object retrieval for `store1`.
