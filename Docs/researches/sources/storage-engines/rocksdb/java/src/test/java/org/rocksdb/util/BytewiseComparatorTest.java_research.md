# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/BytewiseComparatorTest.java

Purpose: Port of comparator DB iteration tests comparing Java bytewise/reverse comparators to RocksDB C++ built-in comparators over randomized write/delete/iterator operations.

Important APIs/types/functions: `BytewiseComparator`, `ReverseBytewiseComparator`, `BuiltinComparator`, `doRandomIterationTest`, `openDatabase`, `toJavaComparator`, nested `KVIter implements RocksIteratorInterface`.

Control flow and state: each test opens a temporary DB with either C++ or Java comparator, builds an equivalent Java `TreeMap`, applies randomized puts/deletes with periodic flushes, then performs randomized iterator operations (`seekToFirst`, `seekToLast`, `seek`, `seekForPrev`, `next`, `prev`, `refresh`) and point gets. RocksDB iterator results are compared to `KVIter`, a reference iterator over the `TreeMap` using the same comparator.

State and persistence behavior: DB state lives on temporary files and may flush to SSTs during tests; the reference `TreeMap` tracks expected logical state. No long-term persistence.

Dependencies and integration points: JNI comparator callbacks, built-in C++ comparator names, Rocks iterator API, flush/write/read options, direct and non-direct comparator buffer modes.

Risks: `KVIter.status()` throws when invalid, whereas RocksDB iterator status can be valid even when positioned invalid; the test calls status before operations and avoids invalid value reads. Random seeds are fixed for reproducibility, but key universe is small.

Test signals: strong behavioral equivalence checks across Java/C++ comparator implementations, reverse ordering, flush boundaries, and iterator navigation.
