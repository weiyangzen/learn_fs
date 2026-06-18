# sources/storage-engines/wiredtiger/test/suite/test_hs31.py

Purpose: ensures no-timestamp removals clear obsolete history-store records once their tombstones become globally visible. It covers column, integer-row, and string-row keys.

Important APIs and functions: `create_key` normalizes string versus numeric keys; `get_stat` reads connection statistics. Scenarios toggle whether globally visible cleanup occurs before a checkpoint. Statistics checked are `cache_hs_key_truncate_onpage_removal` and `rec_hs_wrapup_next_prev_calls`.

Control flow: the test writes timestamped values at timestamps 10 through 14, checkpoints, evicts pages to move history, opens a long-running transaction to pin transaction IDs, removes all keys with `no_timestamp=true`, optionally checkpoints, verifies the long-running reader still sees old content, rolls it back, advances oldest/stable to 10, checkpoints and evicts to remove obsolete entries, inserts new values at timestamp 20, and finally confirms old read timestamps no longer see prior values.

State and persistence behavior: history-store content must remain available while a long transaction pins it, then be truncated after the out-of-order no-timestamp tombstone becomes globally visible.

Dependencies and integration points: integrates no-timestamp tombstones, timestamp history, eviction, checkpoint, and history-store truncation stats.

Risks and edge cases: high row count and many timestamped updates make the test expensive. It depends on stat names and exact cleanup mechanics.

Test signals: old readers initially see `value1`; later reads at timestamps 10-14 return `WT_NOTFOUND`; both history-store cleanup stats are greater than zero.
