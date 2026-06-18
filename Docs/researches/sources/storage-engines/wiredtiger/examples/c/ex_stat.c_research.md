# sources/storage-engines/wiredtiger/examples/c/ex_stat.c

Purpose: demonstrates database, table, session, direct-key, and derived statistics queries.

Important APIs and control flow: helper `print_cursor` iterates a statistics cursor and prints nonzero values. `print_database_stats`, `print_file_stats`, and `print_session_stats` open `statistics:`, `statistics:table:access`, and `statistics:session`. `print_overflow_pages` seeks `WT_STAT_DSRC_BTREE_OVERFLOW`. `get_stat` positions a stats cursor by statistic key. `print_derived_stats` computes fragmentation from checkpoint/file size and write amplification from app bytes versus filesystem writes. `main` opens with `statistics=(all)`, creates `table:access`, inserts one row, checkpoints, prints all categories, and closes.

State and persistence: persists one table and checkpoint. Statistics are runtime/database state and may be cleared or vary by build/configuration.

Dependencies and integration: depends on generated/stat header constants such as `WT_STAT_DSRC_BLOCK_CHECKPOINT_SIZE` and the statistics cursor schemas.

Risks: integer fragmentation calculation uses integer division, so small ratios may truncate. Statistics availability and values depend on configuration and workload; zero values are intentionally suppressed.

Test signals: stats cursors should open and iterate to `WT_NOTFOUND`, direct stat lookup should succeed, and derived-stat calculations should not divide by zero.
