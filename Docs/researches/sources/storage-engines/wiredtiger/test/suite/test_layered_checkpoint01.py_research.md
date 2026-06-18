# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint01.py

Purpose: basic layered-table checkpoint/statistics test for disaggregated leader mode with PALite page log configuration.

Important APIs and functions: decorated with `@disagg_test_class`; `conn_config` enables statistics, JSON stats logging, disaggregated leader role, and a PALite page log. The test uses `statistics:<uri>` and `stat.dsrc.btree_entries`.

Control flow: it creates a layered table, inserts three string-key records per loop for 50,000 loop iterations, scans the table counting all entries, then opens a data-source statistics cursor and checks btree entry count.

State and persistence behavior: layered table state is written under disaggregated storage. The test does not explicitly call checkpoint in the body, so it primarily validates live layered-table insert/read/stat behavior under configured disaggregation.

Dependencies and integration points: integrates layered URI support, disaggregated leader configuration, statistics cursors, and large insert/scan workload.

Risks and edge cases: large `nitems` makes it heavier than a unit smoke test. Without explicit checkpoint, it provides limited checkpoint coverage despite the file name.

Test signals: scan count equals `nitems * 3`, and `stat.dsrc.btree_entries` also equals `nitems * 3`.
