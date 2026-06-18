# sources/storage-engines/wiredtiger/test/csuite/wt10461_skip_list_stress/main.c

Purpose: this white-box stress test reproduces WT-10461, a weak-memory-ordering hazard in skiplist insertion. It stresses `__wt_search_insert` while another thread inserts decreasing keys into the same insert list, looking for assertions that catch inconsistent `next_stack` ordering.

Important APIs, types, and functions: unlike ordinary API tests, it casts `WT_CURSOR` to `WT_CURSOR_BTREE`, sets `WT_SESSION_IMPL.dhandle`, and calls internal `__wt_search_insert` directly. It uses `WT_ITEM` for the probe key, `__wt_thread_create`, atomic counters, `sysconf(_SC_NPROCESSORS_ONLN)`, and `debug_mode=(stress_skiplist=1)`. `insert_key` wraps normal cursor inserts. `thread_search_insert_run` repeatedly builds the search insert stack for key `"00"`. `run` sets up and stresses one insert list.

Control flow: `main` loops `run` for about fifteen minutes. Each run creates a fresh database, creates a table with huge `memory_page_max` to avoid page splitting, inserts boundary keys `"0"` and `"99999"`, starts one search-insert thread per CPU except one, waits until they are active, then inserts 10,000 keys in decreasing order inside one transaction. Search-insert threads stop when `inserts_finished` becomes true.

State and persistence behavior: persistence is not the point; each run creates and removes a temporary home. The important state is in-memory insert list and skiplist pointer ordering under concurrent access. The test intentionally avoids actually inserting the `"00"` probe key in search threads.

Dependencies and integration points: this file depends on WiredTiger internal structures and functions, not just the public API. It also depends on debug stress mode and CPU parallelism to increase race probability. The smoke wrapper runs the binary once, but the binary itself loops for its timed duration.

Risks and test signals: the main risk is relying on internal layout and timing, so it may be expensive or architecture-sensitive. Passing is no assertion or crash for the full duration. A failure usually manifests as an internal assertion in `__wt_search_insert` or related skiplist code.
