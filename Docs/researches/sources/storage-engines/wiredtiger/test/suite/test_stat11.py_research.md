<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat11.py

Purpose: smoke test ensuring selected eviction-blocked connection statistics exist in the Python stat namespace and can be read.

Important APIs/types/functions: `test_stat11` imports `wiredtiger`, opens `statistics:`, and dynamically resolves stat keys from `wiredtiger.stat.conn` names such as `cache_eviction_blocked_checkpoint`, `cache_eviction_blocked_hazard`, and several conflict/block reasons.

Control flow: open a connection statistics cursor and for each stat name fetch `stat_cursor[getattr(wiredtiger.stat.conn, s)][2]`, asserting the value is not `None`.

State and persistence behavior: no workload is required; the test only validates stat registration and cursor access. Values may be zero and are not semantically checked.

Dependencies/integration points: covers the generated Python stat bindings and connection statistics cursor. Risks are limited to renamed/removed stats; signal is successful lookup and non-`None` value for every listed stat.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat11.py -->
