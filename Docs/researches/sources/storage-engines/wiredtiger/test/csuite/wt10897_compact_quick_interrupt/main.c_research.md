# sources/storage-engines/wiredtiger/test/csuite/wt10897_compact_quick_interrupt/main.c

Purpose: this regression test verifies that compact can be interrupted quickly through the general event handler before doing meaningful work, and that a no-work compact reports as skipped rather than interrupted.

Important APIs, types, and functions: it uses `WT_EVENT_HANDLER` with both message and general callbacks, `WT_EVENT_COMPACT_CHECK`, `WT_SESSION::compact`, data-source statistics cursor, and `WT_STAT_DSRC_BTREE_COMPACT_PAGES_REVIEWED`. `populate` inserts random values and a large string payload. `remove_records` creates free space. `message_handler` detects verbose compact messages for "skipping compaction" and "compact interrupted". `handle_general` returns `-1` to interrupt when configured.

Control flow: `main` creates `table:compact`, inserts a small set of records, checkpoints, and runs compact expecting a skipped-compaction message. It then inserts many more records, checkpoints, removes about half the key range, enables interruption, and calls compact again. That call must return `WT_ERROR`, set the interrupted flag, and not set skipped. The test then reads the compact pages reviewed statistic and asserts it is zero. Finally it disables interruption and runs a normal compact successfully.

State and persistence behavior: the test creates a temporary home with 2GB cache and verbose compact logging. It persists enough table data and checkpoints to make compact eligible for real work, then verifies interruption before page review. It removes the home unless preservation is requested.

Dependencies and integration points: it depends on compact verbose messages and data-source statistics names remaining stable. It also depends on the general event callback being invoked early enough in compaction.

Risks and test signals: risks include message text changes, statistic semantics changes, or compaction doing work before the interrupt check. Passing requires the exact assertions around skipped/interrupted flags, return code, and zero pages reviewed.
