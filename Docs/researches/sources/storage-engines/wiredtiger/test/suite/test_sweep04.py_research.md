<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_sweep04.py

Purpose: intended long stress test for whether data-handle sweep keeps up with a workload that continuously drops/creates transient tables while repeatedly accessing a core set; currently skipped due to `FIXME-WT-13706`.

Important APIs/types/functions: module helper `average_slope` computes average and least-squares slope without numpy. `test_sweep04` uses `suite_random`, `stat.conn.dh_conn_handle_count`, `file_open`, many sessions, `session.drop(..., "force")`, and file-manager sweep config.

Control flow: if enabled, the test would create core and transient tables, open 100 sessions, run a long loop whose first half replaces transient tables while occasionally examining them and whose second half only touches core tables, sample dhandle counts every 100 iterations, then compare slopes and end averages.

State and persistence behavior: transient table churn grows and then should shrink in-memory dhandle state as sweep catches up. The slope analysis is the persistent test signal over time rather than a single stat.

Dependencies/integration points: covers sweep behavior under many sessions and handles, random access, forced drops, and statistical trend analysis. Risks are high runtime and flakiness, reflected by the unconditional skip; current signal is the skip, while `average_slope` remains testable utility logic.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep04.py -->
