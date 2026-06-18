<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/insert_stress.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/insert_stress.py

Purpose: stresses insert paths with very large values, mixed key generators, and concurrent transactional reads.

Important APIs and functions: uses direct `Operation.OP_INSERT` variants with uniform and append keys, `Value` sizes 130 KB and 100 bytes, `op_group_transaction` for grouped read transactions, and `Workload`.

Control flow: open a 4 GB cache connection with checkpoint every 10 seconds, snappy compression, disabled logging, and statistics logging; create `file:test.wt` with `leaf_value_max=64MB`; populate 500 rows; define a thread that does a large uniform insert, ten small uniform inserts, and a large append insert; define a read transaction made from 100 search operations; run eight insert threads plus one read thread for 240 seconds.

State and persistence: creates a compressed file table with large values and frequent checkpointing. The table key range is 100 million. No explicit latency output is written.

Dependencies and integration: relies on snappy compressor support and Workgen's large-value generation. Part of stress workload suite.

Risks: large value sizes drive disk and cache pressure. Insert operations with uniform keys may hit duplicate-key or update-like behavior depending on Workgen semantics. No latency file despite benchmark nature.

Test signals: populate and workload assertions, WiredTiger stats log, and checkpoint behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/insert_stress.py -->
