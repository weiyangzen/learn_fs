# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/JNIComparatorTest.java

Purpose: Parameterized test that compares full key iteration order from Java comparators against C++ built-in bytewise and reverse-bytewise comparators.

Important APIs/types/functions: `BuiltinComparator.BYTEWISE_COMPARATOR`, `REVERSE_BYTEWISE_COMPARATOR`, `BytewiseComparator`, `ReverseBytewiseComparator`, `storeWithJavaComparator`, `storeWithCppComparator`, `readAllWithJavaComparator`, `readAllWithCppComparator`.

Control flow and state: for each built-in/directness parameter, the test writes all integers from `Short.MIN_VALUE - 1` to `Short.MAX_VALUE + 1` as 4-byte keys into one DB using the Java comparator and another using the C++ comparator. It then reopens and iterates both DBs, decoding keys into arrays, and asserts identical order.

State and persistence behavior: uses temporary DB directories and close/reopen cycles to validate on-disk order. The declared `useDirectBuffer` parameter is not applied to `ComparatorOptions` in this file, so directness is represented in the parameter name but not in behavior.

Dependencies and integration points: RocksJava comparator JNI and built-in comparator configuration.

Risks: potential test gap: `useDirectBuffer` is unused, so direct comparator callback equivalence is not actually varied here. The key range is large enough for meaningful ordering but still bounded.

Test signals: strong Java-vs-C++ ordering equivalence for bytewise and reverse bytewise comparators, subject to the directness caveat.
