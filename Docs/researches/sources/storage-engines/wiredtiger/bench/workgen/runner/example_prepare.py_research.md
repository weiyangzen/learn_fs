<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_prepare.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/example_prepare.py

Purpose: small prepared-transaction example combining inserts prepared with stable timestamp, updates with commit timestamps, and lagged timestamp reads.

Important APIs and functions: uses `txn`, Workgen transaction attributes `read_timestamp_lag`, `use_prepare_timestamp`, and `use_commit_timestamp`, plus workload timestamp options `oldest_timestamp_lag`, `stable_timestamp_lag`, and `timestamp_advance`.

Control flow: open a 500 MB cache connection; create one string table; populate 5,000 rows; build a read transaction at read timestamp lag 30; build snapshot insert transaction using prepare timestamp; build snapshot update transaction using commit timestamp; run 30 copies of each operation type for 50 seconds; write latency output.

State and persistence: table data persists in WT home for the process. Workgen advances timestamps every second with oldest lag 40 and stable lag 20, supporting prepared/commit timestamp semantics. `latency.out` records operation latency.

Dependencies and integration: simple benchmark/example for Workgen timestamp transaction options; imports `time` only for elapsed time printing.

Risks: small table and high thread count can amplify conflicts or not-found behavior depending on Workgen key generation. Report interval is 500 seconds, longer than run time, so periodic reports are effectively suppressed.

Test signals: populate/workload assertions, elapsed-time print, and latency output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_prepare.py -->
