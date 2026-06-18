# sources/storage-engines/wiredtiger/examples/python/ex_stat.py

Purpose: Python binding example for querying and deriving WiredTiger statistics.

Important APIs and control flow: `main` recreates WT_HOME, opens with `statistics=(all)`, creates `table:access`, writes one row via item assignment, checkpoints, prints `WIREDTIGER_VERSION_STRING`, then calls helper functions. `print_database_stats` and `print_file_stats` open statistics cursors. `print_overflow_pages` indexes the table stats cursor by `stat.dsrc.btree_overflow`. `print_derived_stats` reads block and cursor-byte stats through `stat.dsrc` constants and computes fragmentation and write amplification. `print_cursor` iterates with `next()` and prints nonzero printable values.

State and persistence: creates one table and checkpoint; statistics reflect the runtime/database state after the insert.

Dependencies and integration: depends on Python `wiredtiger` bindings, the `stat` constant namespace, and filesystem cleanup.

Risks: destructive `rm -rf WT_HOME`; no exception-safe cleanup. The fragmentation output format has `%%%s`, resulting in a literal percent sign before the computed value. Statistics values can vary by build and storage behavior.

Test signals: statistics cursors should iterate, direct stat indexing should work, and derived calculations should avoid divide-by-zero guards.
