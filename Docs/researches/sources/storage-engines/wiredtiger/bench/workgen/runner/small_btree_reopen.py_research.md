<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/small_btree_reopen.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/small_btree_reopen.py

Purpose: small btree read workload that forces reopen behavior on each search operation.

Important APIs and functions: same as `small_btree.py`, with direct private assignment `op._config = 'reopen'`.

Control flow: create/populate one table with 500,000 rows; create search operation, set config to `reopen`, run 8 copies for 120 seconds.

State and persistence: persistent table data is repeatedly searched with reopen behavior, likely exercising handle open/close paths.

Dependencies and integration: relies on Workgen interpreting `_config='reopen'`. Used to compare normal read path versus reopen overhead.

Risks: direct mutation of private `_config` is fragile. No latency file. Reopen behavior can be much slower and file-manager sensitive.

Test signals: assertions and workload reports.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/small_btree_reopen.py -->
