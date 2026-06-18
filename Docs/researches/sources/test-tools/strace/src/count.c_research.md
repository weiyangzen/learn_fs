<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/count.c -->
## sources/test-tools/strace/src/count.c

Purpose: Maintains and prints strace syscall summary statistics for `-c` style counting, including optional wall-clock columns and unknown syscall buckets.

Important APIs and types: `struct call_counts`, `struct unknown_call_counts`, `struct unknown_call_bucket`, `enum count_summary_columns`, `count_syscall`, `set_sortby`, `set_count_summary_columns`, `set_overhead`, and `call_summary`.

Control flow: `count_syscall` ensures a per-personality count vector exists, inserts unknown syscall buckets when needed, updates call/error counts, computes elapsed syscall time using either wall-clock or system CPU time, subtracts configured overhead, clamps negative durations to zero, and optionally tracks wall-clock stats separately. Sorting functions compare totals, min/max/avg, calls, errors, names, and wall columns. `set_sortby` and `set_count_summary_columns` parse user aliases. `call_summary` iterates personalities, calls `call_summary_pers`, and restores the original personality.

State and persistence: Global `countv[]`, `unknown_countv[]`, `overhead`, column configuration, wall-column flags, and `sortfun` persist for the process. Unknown syscall buckets grow dynamically and store synthetic names.

Dependencies and integration: Depends on `defs.h`, `xstring.h`, timespec helpers, personality/sysent tables, `count_wallclock`, syscall entry/exit timestamps in `tcb`, and output `FILE *`.

Risks: Summary output assumes at least one call when printing totals; empty vectors are skipped. Column parsing rejects duplicates and unknown names. Unknown syscall indices combine known syscall count with bucket index, so helper lookup must distinguish real scno from synthetic positions.

Test signals: Tests should cover sorting by every alias family, duplicate/unknown columns, wall columns with and without `count_wallclock`, overhead subtraction, negative elapsed clamp, unknown syscall naming, multi-personality summaries, and zero-error rows.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/count.c -->
