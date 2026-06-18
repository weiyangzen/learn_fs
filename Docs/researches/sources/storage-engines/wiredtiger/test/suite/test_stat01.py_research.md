<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat01.py

Purpose: foundational statistics cursor tests for connection stats, data-source stats, checkpoint-specific stats, size stats, and missing-file error handling.

Important APIs/types/functions: `test_stat01` uses `wiredtiger.stat`, `SimpleDataSet`, `simple_key`, `make_scenarios`, helper `statstr_to_int`, and `check_stats`. Scenarios cover file/table URIs and column/string-row keys.

Control flow: connection stats populate and checkpoint a dataset, scan `statistics:` entries for block writes, and verify keyed lookup consistency. Data-source stats create overflow-prone values, reopen, inspect page-size and overflow stats, check backup stats are readable, and open a size-only stats cursor. Checkpoint stats create named checkpoints and verify entry counts per checkpoint. Missing-file stats expects an open failure.

State and persistence behavior: reopen and named checkpoint paths validate stats from persisted btree state and checkpoint metadata. String stat values are parsed and compared to integer stat fields.

Dependencies/integration points: covers connection, dsrc, checkpoint, and size statistics APIs plus dataset helpers. Risks include stat descriptions changing and timestamp hook skip on checkpoint stats; signals are found stats, min thresholds, self-consistent value strings, and expected errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat01.py -->
