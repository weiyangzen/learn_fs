<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat02.py

Purpose: comprehensive statistics cursor configuration tests: database-level enabled modes, cursor mode compatibility, clear behavior, fast-vs-all collection, invalid mode combinations, and cache/tree walk options.

Important APIs/types/functions: the file defines several test classes using `SimpleDataSet`, `ComplexDataSet`, `make_scenarios`, `wiredtiger.stat`, and `wiredtiger_open`. It exercises `statistics=(none|fast|all|size|clear|cache_walk|tree_walk)` at connection and cursor scope.

Control flow: scenario tests populate data and verify which cursor configurations open or fail. Clear tests read stats twice to confirm selected counters reset while others persist. Fast tests confirm btree entry counts are omitted from fast cursors and present in all cursors. Error tests reject conflicting statistics modes. Cache-walk tests reconfigure live connections and assert cache/tree walk stats appear independently.

State and persistence behavior: statistics state is mutable and sometimes cleared on cursor open; populated datasets provide counters. Cache-walk stats can persist because many are not clearable, so the test orders cases carefully.

Dependencies/integration points: covers connection open config parsing, session cursor config parsing, dsrc stats, cache walk, tree walk, and complex dataset index/colgroup behavior. Risks include ordering-sensitive clear semantics and exact error regexes; signals are successful/failed cursor opens and precise stat values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat02.py -->
