<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_stat.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_stat.c

Purpose: Implements `wt stat`, printing connection or object statistics as `description=value` lines.

Important APIs/functions: `usage` documents `stat [-f] [uri]` and compatibility `-a` is accepted in parsing. `util_stat` resolves optional object URI, constructs `statistics:<object>` with `__wt_snprintf`, opens a statistics cursor with optional `statistics=(fast)`, iterates with `cursor->next`, and reads `desc` and printable value via `cursor->get_value`.

Control flow: No operand selects connection statistics (`statistics:`). One operand selects table statistics after `util_uri(..., "table")`. More operands fail usage. Iteration stops on `WT_NOTFOUND`, which is normalized to success. Errors during allocation, cursor open, printf, or cursor get go to a common `err` block that returns `1`.

State and persistence behavior: Read-only. It allocates temporary strings for object and statistics URIs and opens a cursor; no durable database state is changed. Fast statistics may avoid expensive gathering and can therefore report a subset.

Dependencies and integration points: Depends on WiredTiger statistics cursors, utility allocation wrappers, URI resolution, and global program name. It is integrated into monitoring/support workflows that scrape utility output.

Risks: The `-a` option is silently retained for compatibility but no longer changes behavior, which can confuse older scripts. It does not explicitly close the cursor in this function. Output descriptions are human-oriented strings, so consumers relying on exact text are sensitive to WiredTiger stat-description changes.

Test signals: Tests should cover connection versus table statistics URIs, `-f` config, compatibility `-a`, allocation/format failures by injection, and stable handling of `WT_NOTFOUND`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_stat.c -->
