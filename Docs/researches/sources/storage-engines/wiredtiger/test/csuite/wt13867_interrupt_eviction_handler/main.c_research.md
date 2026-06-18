# sources/storage-engines/wiredtiger/test/csuite/wt13867_interrupt_eviction_handler/main.c

Purpose: this test verifies that application eviction callbacks can interrupt eviction and that WiredTiger statistics classify interrupted application cache operations as busy/uninterruptible rather than idle/interruptible.

Important APIs, types, and functions: it uses a `WT_EVENT_HANDLER` general callback for `WT_EVENT_EVICTION`, a tiny `cache_size=1MB`, connection statistics, and internal statistic keys `WT_STAT_CONN_APPLICATION_CACHE_OPS`, `WT_STAT_CONN_APPLICATION_CACHE_UNINTERRUPTIBLE_OPS`, `WT_STAT_CONN_APPLICATION_CACHE_INTERRUPTIBLE_OPS`, `WT_STAT_CONN_CACHE_BYTES_MAX`, and `WT_STAT_CONN_CACHE_BYTES_INUSE`. `populate` inserts random keys with 1KB values to create cache pressure. Macros `GET_STAT`, `GET_STATS`, and `GET_ALL_STATS` collect counters.

Control flow: `main` opens the database, creates `table:evict`, records the application session in `my_session`, and first populates until enough cache operations occur without interruption. It asserts the eviction callback ran, both busy and idle counters sum to total cache operations, and cache size stats are nonzero. It then enables `do_interrupt_eviction`, populates again until enough additional cache operations occur, and asserts busy operations increased while idle operations did not.

State and persistence behavior: the table persists only within a temporary home. The durable data is less important than forcing cache pressure and eviction. The core mutable state is the event-handler return value and the connection statistics counters.

Dependencies and integration points: it relies on eviction event callbacks being delivered to the application session rather than internal sessions, verified by `session == my_session`. It also relies on stable statistics semantics for application cache operation classification.

Risks and test signals: risk areas include cache pressure being insufficient on a platform, event callbacks changing session attribution, or statistics names/meanings changing. The loops double work up to a bounded cycle count to reduce flakiness. Passing requires all assertions and cleanup to complete.
