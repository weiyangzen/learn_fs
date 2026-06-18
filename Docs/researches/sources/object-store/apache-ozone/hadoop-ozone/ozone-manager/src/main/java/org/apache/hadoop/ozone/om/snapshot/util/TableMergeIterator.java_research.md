## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/util/TableMergeIterator.java

Purpose: iterator that takes a sorted/filter key stream and returns that key with values from multiple RocksDB-backed tables, using null for missing table entries.

Important APIs and types: generic `TableMergeIterator<K extends Comparable<K>, V>` implements `ClosableIterator<Table.KeyValue<K,List<V>>>`; constructor accepts `keysToFilter`, a seek prefix, and varargs tables; `hasNext`, `next`, and `close` implement iteration.

Control flow: each table iterator is opened at the prefix. For every filter key, `updateAndGetValueAtIndex` seeks a table iterator when its cached key is behind the requested key, caches the next KV, and returns the value only on exact key match. `next` reuses a mutable `nextValues` list and wraps it with `Table.newKeyValue`.

State and persistence: maintains table iterators, cached key-values per table, and a reusable values list. It only reads tables.

Dependencies and integration: used by snapshot diff object-map construction and snapshot defrag SST spill logic to compare values between snapshot tables for candidate SST keys.

Risks and test signals: returned value lists are mutable and reused on the next `next` call, so callers must copy if retaining. It assumes the filter key stream is ordered compatibly with table iterators; out-of-order keys can force seeks but may still work less efficiently. Exceptions during seek are wrapped as `UncheckedIOException`. Tests should cover missing entries, exact matches across multiple tables, mutable-list reuse, prefix seeks, out-of-order or duplicate filter keys, close closing all iterators, and seek exception propagation.
