<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/InMemoryTestTable.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/InMemoryTestTable.java

Purpose: generic in-memory `Table<KEY,VALUE>` implementation for tests that need simple table semantics without RocksDB.

Important APIs/types/functions: constructors from name/map, `put`, `isEmpty`, `isExist`, `get`, `getIfExist`, `delete`, `deleteRange`, `getName`, `getEstimatedKeyCount`, `getMap`, and unsupported `Table` operations such as batch writes, iterators, range queries, prefix deletes, dump/load.

Control flow: constructors copy supplied values into a `ConcurrentSkipListMap`. Basic CRUD methods delegate directly to the map. `deleteRange` clears a sub-map. Unsupported methods throw `UnsupportedOperationException`.

State and persistence behavior: state is a concurrent sorted in-memory map. There is no durable persistence, batching, or file dump/load behavior.

Dependencies and integration points: implements the HDDS `Table` interface and is extended by `StringInMemoryTestTable` to provide string-key iteration.

Risks: only a subset of `Table` behavior is implemented; tests using unsupported methods will fail fast. `ConcurrentSkipListMap` requires comparable keys or compatible ordering.

Test signals: no direct tests in this file; correctness is observed through tests that use the in-memory table as a fixture.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/InMemoryTestTable.java -->
