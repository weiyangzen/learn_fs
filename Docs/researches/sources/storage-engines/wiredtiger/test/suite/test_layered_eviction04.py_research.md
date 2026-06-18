# sources/storage-engines/wiredtiger/test/suite/test_layered_eviction04.py

Purpose: verifies that closing/verifying a file with pages not yet materialized fails rather than silently evicting unsafe pages.

Important APIs and functions: `test_layered_eviction04` uses leader disaggregated config, layered table creation, timestamped writes, `conn.set_context_uint`, page-log `pl_set_last_materialized_lsn`, `session.verify`, `assertRaises`, and `wiredtiger.WiredTigerError`.

Control flow: the test creates and populates a layered table, checkpoints, manipulates materialization LSN state so pages are considered not fully materialized, and then attempts operations such as verify/close that force eviction or file cleanup. It asserts the expected error path is taken.

State and persistence behavior: page data exists in the page log, but the materialization frontier says it is not safe to evict/close. The test ensures the system preserves safety by returning an error rather than discarding or closing around unmaterialized pages.

Dependencies and integration: integrates page-log frontier context, layered table lifecycle, verify/close behavior, and Python exception assertions. Risks include silent data loss during file close, frontier checks being bypassed by verify, or errors being swallowed. Test signals are explicit `WiredTigerError` assertions plus successful setup writes and checkpointing.
