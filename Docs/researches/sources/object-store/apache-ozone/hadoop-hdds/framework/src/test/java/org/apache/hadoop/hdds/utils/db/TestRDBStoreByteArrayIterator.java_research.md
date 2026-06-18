# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBStoreByteArrayIterator.java

Purpose: Specifies expected behavior for `RDBStoreByteArrayIterator`, the byte-array iterator wrapper around RocksDB iterators.

Important APIs/types/functions: `RDBStoreByteArrayIterator`, `ManagedRocksIterator`, `RDBTable`, `IteratorType` (`NEITHER`, `KEY_ONLY`, `VALUE_ONLY`, `KEY_AND_VALUE`), `seek`, `seekToFirst`, `seekToLast`, `removeFromDB`, `forEachRemaining`, `hasNext`, and `next`.

Control flow: Mockito stubs `RocksIterator` validity, keys, and values. Tests verify constructor seeking, forward iteration, `hasNext` invalidation behavior, ordered RocksDB calls during `next`, seek semantics, removal through the owning table, close propagation, prefix-specific seek behavior, and unsupported `seekToLast` for prefixed iterators.

State and persistence behavior: No real RocksDB persistence is used; state is simulated through mocked iterator sequences. `removeFromDB` is the only path that mutates a mocked table.

Dependencies and integration points: Integrates RocksDB iterator API with HDDS `Table.KeyValue` abstraction and table deletion. Uses Mockito in-order verification and log-level adjustment for managed object diagnostics.

Risks: Mocked iterator behavior can diverge from native RocksDB edge cases. Prefix tests only validate a key equal to the prefix, not keys that merely start with it.

Test signals: Strong call-order signal for iterator correctness, iterator type key/value read flags, table deletion delegation, and prefix iterator restrictions.
