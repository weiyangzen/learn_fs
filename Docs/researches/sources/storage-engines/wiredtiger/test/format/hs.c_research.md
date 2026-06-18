# sources/storage-engines/wiredtiger/test/format/hs.c

Purpose: optional background thread that scans WiredTiger history store cursors to exercise internal ordering checks while the workload mutates data.

Important APIs and functions: `hs_cursor`, `__wt_curhs_next_hs_id`, `__wt_curhs_open_ext`, cursor `next/prev/get_key/get_value/close`, and session wrapper/prefetch helpers. It is disabled at compile time for WiredTiger major versions below 10.

Control flow: opens one session, loops until `g.workers_finished`, enumerates history store ids, opens each HS cursor, sets read-committed cursor flags, chooses forward or reverse traversal, performs 1,000 to 100,000 steps, tolerates `WT_NOTFOUND`, `WT_CACHE_FULL`, and `WT_ROLLBACK`, closes the cursor, then sleeps 1 to 10 seconds in short intervals.

State and persistence: it does not intentionally mutate user data, but it reads internal history store records and can pin/cache pages transiently. It stores decoded key/value components only in local variables.

Dependencies and integration: spawned from `operations` when `GV(OPS_HS_CURSOR)` is enabled. It relies on WiredTiger internal history-store cursor APIs, `g.wts_conn`, `g.extra_rnd`, and `session_prefetch_cfg`.

Risks and test signals: because this intentionally uses internal APIs and cursor flags, version drift is a risk. Expected transient returns are cache/rollback/notfound; any other cursor error is a failure signal. It can reveal ordering bugs through WiredTiger diagnostic assertions rather than application-level comparisons.
