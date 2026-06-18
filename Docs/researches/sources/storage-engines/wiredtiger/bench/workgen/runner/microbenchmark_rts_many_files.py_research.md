<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_many_files.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_many_files.py

Purpose: RTS/checkpoint microbenchmark for a very large number of files/tables.

Important APIs and functions: direct `Session.create`, cursors, debug eviction cursor `release_evict`, `Operation.OP_CHECKPOINT`, `Operation.OP_RTS`, and latency output.

Control flow: create 100,000 tables named `table:rts_many_filesN`; insert one row into each; evict each row through a debug cursor; run a Workgen workload containing checkpoint then RTS; write `rts_many_files.out`; optionally display data using imported `show`.

State and persistence: creates many WiredTiger table files and associated metadata. Eviction tries to remove pages from cache before checkpoint/RTS measurement.

Dependencies and integration: imports helpers from `microbenchmark_rts_unstable_content`, though timestamps are not used. Stresses metadata/file traversal rather than value volume.

Risks: 100,000 tables can exceed filesystem, metadata, open cursor, or time budgets. The transaction commit condition checks `if i % 56 == 0` inside the row loop, using table index instead of row index; with `nrows=1` this is harmless but odd. `show(uri, session, ...)` targets base URI without suffix, likely not an existing table.

Test signals: workload assertion, no eviction search exceptions, and `rts_many_files.out`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_many_files.py -->
