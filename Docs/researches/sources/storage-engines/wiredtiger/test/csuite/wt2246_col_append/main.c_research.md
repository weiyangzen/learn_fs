# sources/storage-engines/wiredtiger/test/csuite/wt2246_col_append/main.c

Purpose: this WT-2246 performance regression test stresses column-store append cursors. It targets an inefficiency where append cursor record-number allocation searched the target leaf page unnecessarily.

Important APIs, types, and functions: it uses WiredTiger append cursors (`open_cursor(..., "append", ...)`), recno `key_format=r`, string values, test utility append thread `thread_append`, signal handling, and test option fields such as `n_append_threads`, `nrecords`, and `max_inserted_id`. `page_init` preloads enough records to create existing pages before the timed append workload. `onsig` flips `opts->running` on SIGINT.

Control flow: `main` sets defaults of six append threads and 20 million records, opens a 2GB-cache database with eviction threads, creates a column-store table, and calls `page_init(5000)`. It then closes and reopens the connection to force state to disk, installs SIGINT handling, starts append worker threads, joins them, and prints processor seconds per million records inserted.

State and persistence behavior: the test persists a column-store table with appended string records. `page_init` obtains allocated record numbers through `cursor->get_key` after each append and stops after reaching the target. The main workload advances `opts->max_inserted_id` through shared test utility append code.

Dependencies and integration points: it depends on shared csuite test utility code providing `thread_append` and interpreting `TEST_OPTS` fields. It is benchmark-like and integrates with general table type and home parsing.

Risks and test signals: there is no hard assertion on performance. Regression signal is excessive runtime or CPU use, while correctness failures appear as API errors or thread failures. Because it relies on time/CPU output, comparisons should be made under controlled conditions.
