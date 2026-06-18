# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/IntComparatorTest.java

Purpose: Parameterized test for RocksJava `IntComparator` and the JNI comparator callback path using random signed integer keys.

Important APIs/types/functions: `IntComparator`, `ComparatorOptions`, `ReusedSynchronisationType`, `testRoundtrip`, `testRoundtripCf`, RocksDB default and named column family opens.

Control flow and state: the class generates 500 unique 4-byte signed integer keys. For each buffer/synchronization parameter set, it opens a DB or named CF with `IntComparator`, writes all keys, reopens with the same comparator, iterates in order, decodes each key to `int`, and asserts strict ascending order with exactly `TOTAL_KEYS` entries.

State and persistence behavior: temporary DB files are reopened to validate persisted comparator metadata and ordering. CF handles/options are explicitly closed after use.

Dependencies and integration points: exercises Java comparator callbacks across direct and heap buffers, reused JNI buffer strategies, and column family comparator configuration.

Risks: random key generation is unseeded. Comparator compatibility depends on reopening with the same comparator object/configuration; opening with a mismatched comparator would be outside this test. Native direct buffer reuse synchronization is only indirectly stressed by single-thread iteration.

Test signals: strong signal for signed integer ordering, comparator callback correctness, and CF round-trip behavior.
