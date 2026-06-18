<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_overflow_pages.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_overflow_pages.py

Purpose: RTS microbenchmark focused on overflow pages by using tiny page sizes and values large enough to overflow.

Important APIs and functions: direct timestamped writes, `debug=(release_evict)`, `Operation.OP_RTS`, and latency output.

Control flow: open database and set stable timestamp 5; create table with 512-byte allocation and leaf pages; insert 550,000 rows at timestamp 10 with repeated string values; evict rows; checkpoint; run a Workgen RTS operation and write `rts_overflow_pages.out`.

State and persistence: creates overflow-page-heavy on-disk state and unstable timestamped data relative to stable timestamp. RTS should process these unstable updates.

Dependencies and integration: imports `timestamp_str` and `show` helpers. Integrates with other RTS microbenchmarks as a latency-output comparator.

Risks: row-by-row eviction and small pages are expensive. Stable timestamp remains 5 while writes are at 10, so all content is unstable; any semantic expectation should account for full rollback potential. Output file is relative.

Test signals: workload assertion, no eviction failure exceptions, latency file, and optional verbose display.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_overflow_pages.py -->
