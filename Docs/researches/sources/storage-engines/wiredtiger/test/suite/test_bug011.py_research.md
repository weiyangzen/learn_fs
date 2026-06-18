# sources/storage-engines/wiredtiger/test/suite/test_bug011.py

Purpose: long-running eviction stress test for more trees than the eviction server can walk simultaneously. It opens 2,000 tables, more than the built-in 1,000-tree walk limit described in the comments, and repeatedly searches across all of them.

Important APIs/types/functions: `SimpleDataSet`, `wttest.longtest`, `conn_config` returning `cache_size=1GB`, `reopen_conn`, cursor `set_key`, `search`, and `reset`.

Control flow: create and populate 2,000 small-page tables with 10,000 rows each; reopen to force on-disk trees; open one cursor per table to keep handles active; run 10,000 outer operations, searching a random row in every table on each pass.

State/persistence behavior: table pages are persisted before the main loop, then repeatedly faulted/searched/reset under cache pressure. The state under test is hazard-pointer allocation and eviction traversal over many open btrees.

Dependencies/integration: uses `random` for access spread and `SimpleDataSet` key generation. It is explicitly marked `longtest`, so normal quick runs may skip it.

Risks/test signals: extremely expensive; primary signal is survival without eviction failures, hazard pointer exhaustion, crashes, or search errors.
