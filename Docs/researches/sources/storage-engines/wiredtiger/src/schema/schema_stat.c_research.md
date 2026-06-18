# sources/storage-engines/wiredtiger/src/schema/schema_stat.c

Purpose: initializes statistics cursors for schema-level objects by resolving table, column-group, and index URIs to the underlying statistics sources and aggregating component statistics when needed.

Important APIs and functions: `__wt_curstat_colgroup_init`, `__wt_curstat_index_init`, and `__wt_curstat_table_init` are the public initialization helpers. The static `__curstat_size_only` implements a fast path for table size-only stats on simple tables.

Control flow: column-group and index stats resolve the schema object, build `statistics:<source>`, and delegate to `__wt_curstat_init`. Table stats first try the size-only fast path when `WT_STAT_TYPE_SIZE` is set: it reads table metadata directly, confirms there are no named columns, detects layered tables, builds the underlying local filename or disaggregated stable-file URI, and asks the local/disagg size helper. If fast path does not complete, normal table stats open the table. Simple tables redirect to their single column group's statistics. Complex tables open statistics cursors for each column group, copy the first stats block, aggregate subsequent column groups and indexes, and finalize the aggregate.

State and persistence behavior: read-only with respect to metadata and data files. It initializes in-memory cursor stats structures and may open/close component statistics cursors. The fast path avoids schema/table-list locks when possible to reduce pressure under workloads with many create/drop operations.

Dependencies and integration points: depends on schema object lookup helpers, metadata search/config parsing, table open/index open code, statistics cursor initialization/open APIs, local and disaggregated size helpers, and data-source statistics aggregation/finalization functions.

Risks: the size-only fast path infers simple-table layout from metadata and must fall back cleanly on concurrent schema changes or unsupported layouts. Complex aggregation assumes compatible `WT_DSRC_STATS` layouts across column groups and indexes. Layered table size naming must match stable constituent metadata conventions.

Test signals: stats on column groups, indexes, simple tables, complex tables with multiple column groups and indexes, size-only fast path success/fallback, concurrent create/drop fallback, layered/disaggregated size stats, and aggregate finalization correctness.
