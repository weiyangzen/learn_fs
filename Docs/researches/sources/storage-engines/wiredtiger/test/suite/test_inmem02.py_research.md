# sources/storage-engines/wiredtiger/test/suite/test_inmem02.py

Purpose: verifies that an in-memory database permits updates beyond the nominal cache size up to the configured allowance rather than failing too early.

Important APIs and functions: `conn_config` enables `in_memory=true` with a 3MB cache and small pages. The test uses `SimpleDataSet`, large values, and `WT_CACHE_FULL` handling.

Control flow: `test_insert_over_allowed` creates/populates an in-memory table and writes enough data to exceed ordinary cache expectations while staying within the special in-memory allowance. It checks that inserts succeed until the intended threshold and that the cache-full condition is not raised prematurely.

State and persistence behavior: the state under test is in-memory cache accounting and the allowance for over-capacity operations. There is no disk persistence path.

Dependencies and integration points: integrates cache sizing, in-memory storage mode, table page sizing, and cursor writes.

Risks and edge cases: sensitive to exact memory accounting and build configuration. Small cache sizes make this a targeted stress test rather than a general workload.

Test signals: inserts complete as allowed, and any `WT_CACHE_FULL` behavior must align with the expected over-capacity threshold.
