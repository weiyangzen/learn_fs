# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/ReverseBytewiseComparatorIntTest.java

Purpose: Parameterized test verifying `ReverseBytewiseComparator` produces descending integer order for positive 4-byte keys in default and named column families.

Important APIs/types/functions: `ReverseBytewiseComparator`, `ComparatorOptions`, `ReusedSynchronisationType`, `testRoundtrip`, `testRoundtripCf`.

Control flow and state: generates 500 unique positive integer keys, writes them under a reverse bytewise comparator, reopens the DB/CF, iterates from first to last, decodes keys to ints, and asserts each key is less than the previous key. The parameter matrix covers direct/non-direct buffers, reused-buffer sizes, and synchronization modes.

State and persistence behavior: temporary DB state is persisted across close/reopen to validate comparator configuration and ordering.

Dependencies and integration points: RocksJava comparator callbacks, column family APIs, direct buffer JNI paths, and comparator option reuse behavior.

Risks: random key generation is unseeded; only positive ints are used, reducing coverage of bytewise ordering for negative signed representations. Multi-thread reuse behavior is not directly stressed.

Test signals: good reverse-order signal for both default and named CFs under multiple comparator buffer configurations.
