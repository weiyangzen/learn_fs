<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/StringInMemoryTestTable.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/StringInMemoryTestTable.java

Purpose: string-key specialization of `InMemoryTestTable` that adds iterator support via `MapBackedTableIterator`.

Important APIs/types/functions: constructors mirroring the parent table and override `iterator(String prefix, IteratorType type)`.

Control flow: construction delegates to the parent. Calling `iterator` returns a new `MapBackedTableIterator` over the parent `getMap()` and requested prefix; the `IteratorType` argument is accepted but not used.

State and persistence behavior: state is inherited in-memory `ConcurrentSkipListMap` content. Iterators read from that map and provide prefix-filtered traversal.

Dependencies and integration points: integrates test `Table` consumers needing string-key iteration with `MapBackedTableIterator`.

Risks: iterator type is ignored, so tests depending on different iterator modes are not modeled. Prefix filtering behavior inherits the iterator caveats around `seek`.

Test signals: no direct tests in this file; it is a fixture for DB/table tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/StringInMemoryTestTable.java -->
