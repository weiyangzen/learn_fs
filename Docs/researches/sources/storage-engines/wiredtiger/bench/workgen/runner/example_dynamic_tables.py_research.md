<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_dynamic_tables.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/example_dynamic_tables.py

Purpose: demonstrates Workgen dynamic table creation and deletion while workload operations target random tables.

Important APIs and functions: uses `Context`, `Key`, `Value`, `Operation`, `Thread`, and `Workload`. The key distinction is constructing operations without an explicit `Table`, letting Workgen select random dynamic tables. Workload options `create_prefix`, `create_interval`, `create_count`, `create_trigger`, `create_target`, `max_num_files`, `drop_interval`, `drop_count`, `drop_trigger`, and `drop_target` drive dynamic DDL.

Control flow: open a default WT home, build random-table insert/update/search threads, create a workload running for 300 seconds, configure creation when database size falls below 100 MB until 200 MB, configure drops when size exceeds 250 MB until 75 MB, then run.

State and persistence: dynamically creates and drops tables with prefix `dynamic_` in the WiredTiger home. The workload state is driven by database size thresholds and maximum file count.

Dependencies and integration: validates Workgen dynamic table features rather than a specific WT storage algorithm. It can pair with `validate_mirror_tables.py` when dynamic mirroring is enabled elsewhere, though this file does not enable mirrors directly.

Risks: operations on random tables depend on Workgen's dynamic-table state; empty table sets during startup/shutdown could expose edge cases. Size thresholds are workload-environment dependent.

Test signals: single `assert ret == 0`, successful dynamic DDL over 300 seconds, and absence of Workgen errors while tables are changing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_dynamic_tables.py -->
