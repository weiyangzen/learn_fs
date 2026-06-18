# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/BytewiseComparatorIntTest.java

Purpose: Parameterized RocksJava test that verifies `BytewiseComparator` orders positive 4-byte integer keys consistently across default and named column families.

Important APIs/types/functions: `BytewiseComparator`, `ComparatorOptions.setUseDirectBuffer`, `setMaxReusedBufferSize`, `setReusedSynchronisationType`, `testRoundtrip`, `testRoundtripCf`, and parameter sets for direct/non-direct, reused buffer size, and synchronization type.

Control flow and state: `prepareKeys()` creates 500 unique positive integer keys as big-endian byte arrays. Each test builds comparator options from parameters, opens a DB with the comparator, writes all keys, reopens, iterates from first to last, decodes keys with `ByteBuffer`, and asserts strictly increasing integer order. The CF variant puts data into a named column family configured with the comparator and repeats the reopen/iterate check.

State and persistence behavior: temporary DB files persist across close/reopen inside each test to confirm comparator identity/order metadata works after reopening.

Dependencies and integration points: RocksJava comparator JNI, `RocksNativeLibraryResource`, column family descriptors/options, direct buffer callback paths, and comparator reused-buffer synchronization strategies.

Risks: random keys are non-deterministic because no seed is set. It only uses positive ints, avoiding signed-byte ordering pitfalls for negative values. CF option handles must be closed carefully.

Test signals: strong signal for comparator round-tripping, CF integration, and direct versus heap callback compatibility.
