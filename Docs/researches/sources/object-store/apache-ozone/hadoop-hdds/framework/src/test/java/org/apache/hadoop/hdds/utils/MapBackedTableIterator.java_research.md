<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/MapBackedTableIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/MapBackedTableIterator.java

Purpose: reusable unit-test implementation of `Table.KeyValueIterator<String,V>` over a `NavigableMap`, with optional prefix filtering.

Important APIs/types/functions: constructor `MapBackedTableIterator(NavigableMap<String,V>, String)`, `seekToFirst`, `seekToLast`, `seek`, `hasNext`, `next`, `removeFromDB`, `close`, and `Table.newKeyValue`.

Control flow: construction stores the map/prefix and calls `seekToFirst`. `seekToFirst` streams all entries, filters by prefix, maps entries to `Table.KeyValue` with value-size metadata, and installs an iterator. `seekToLast` delegates to `seek(values.lastKey())`. `seek` filters by prefix and key >= target, installs a new iterator, and returns the map ceiling entry for the target.

State and persistence behavior: iterator state is the current Java iterator over a snapshot stream pipeline. The backing map remains external and in-memory. `removeFromDB` and `close` are no-ops.

Dependencies and integration points: integrates test maps with the HDDS `Table` iterator contract and is used by `StringInMemoryTestTable`.

Risks: `seek` returns `values.ceilingEntry(s)` without applying the prefix filter to the returned value, while the installed iterator does filter; this can differ when a target key ceiling does not match the prefix. `seekToLast` on an empty map will throw due to `lastKey`.

Test signals: no direct tests in this file; behavioral validation is indirect through consumers of in-memory test tables.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/MapBackedTableIterator.java -->
