## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MultiGetManyKeysTest.java

### Purpose

`MultiGetManyKeysTest` stresses `multiGetAsList` and transactional multi-get APIs with very large key-list sizes, including 750,000 keys on 64-bit systems.

### Important APIs, Types, And Functions

It uses `RocksDB.multiGetAsList`, `Transaction.multiGetAsList`, `Transaction.multiGetForUpdateAsList`, CF variants of those methods, `TransactionDB.open`, `ColumnFamilyDescriptor`, and helper methods for random key/value generation. The private `Key` wrapper provides content-based equality and hashing for `byte[]` keys.

### Control Flow

Parameterized tests generate random four-byte keys, randomly assign values to about 10 percent of them, write those values to the DB or a non-default CF, reopen as plain or transactional DB, perform multi-get, and compare every returned position to the expected map. A `BeforeClass` assumption skips the class on 32-bit systems.

### State And Persistence Behavior

Data is written in one DB handle and read after reopening, so values must survive close/open and be addressable by large Java collections. Transactional variants read without committing modifications, but `multiGetForUpdateAsList` also exercises lock/conflict bookkeeping paths.

### Dependencies And Integration Points

This integrates Java collection marshalling, native batch point lookup, transaction DB wrappers, CF handle lists sized to the key list, and platform detection via `org.rocksdb.util.Environment`.

### Risks And Edge Cases

- Four-byte random keys can collide; the map and DB overwrite semantics use the later value, but duplicate keys can make coverage less uniform.
- Very large lists stress JNI array/list conversion, native vector sizing, memory pressure, and 32-bit size limits.
- CF tests depend on matching every key with the same CF handle and closing handles after transaction use.

### Test Signals

The returned value list size must equal the key list size, and each element must match the stored byte array or `null`. Static research only; no test command was run.
