<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/small_update_reopen.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/small_update_reopen.py

Purpose: small update workload using reopen operation config, with raw byte key/value formats.

Important APIs and functions: uses `key_format=u,value_format=u`, insert/update operations, `op._config='reopen'`, and Workgen thread multiplication.

Control flow: open 500 MB cache; create `file:test.wt`; populate 500,000 rows with 200-byte values; run 8 update threads with reopen config for 120 seconds.

State and persistence: updates a persistent table while reopening handles/cursors per operation according to Workgen config.

Dependencies and integration: companion to small btree reopen read benchmark.

Risks: private `_config` mutation, no latency output, and update conflicts/overwrites may vary with key generator behavior.

Test signals: populate/workload assertions and Workgen report output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/small_update_reopen.py -->
