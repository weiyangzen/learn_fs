# sources/storage-engines/wiredtiger/test/format/format_prepare_discover.c

Purpose: implements `wts_prepare_discover`, a restart/open-time cleanup path for preserved prepared transactions when precise checkpoint and prepared-operation testing are both enabled. It opens a `prepared_discover:` cursor, claims each discovered prepared transaction by `claim_prepared_id=<id>`, then randomly resolves it as committed or rolled back.

Important APIs and functions: `WT_CONNECTION::open_session`, `WT_SESSION::open_cursor`, `WT_CURSOR::next/get_key/close`, `WT_SESSION::begin_transaction`, `timestamp_transaction_uint` for commit/durable/rollback timestamps, `commit_transaction`, `rollback_transaction`, `checkpoint`, `wts_verify_mirrors`, and format helpers such as `trace_msg`, `mmrand`, and `testutil_check`.

Control flow: the function returns immediately unless `GV(PRECISE_CHECKPOINT)` and `GV(OPS_PREPARE)` are set. It opens a session and discover cursor, treats `WT_NOTFOUND` from open as the normal no-work case, allocates a future timestamp via `g.timestamp += 10`, iterates all cursor entries, claims each prepared id, commits roughly half and rolls back the rest, checkpoints, then verifies mirrors against `WiredTigerCheckpoint` unless disaggregated storage disables checkpoint cursors.

State and persistence: it mutates `g.timestamp`, resolves prepared durable state that persisted across checkpoint/restart, and creates a checkpoint after resolution. The resolved prepared ids are removed from the prepared-discover stream by WiredTiger claim semantics. Mirror verification observes checkpoint state and disagg mode.

Dependencies and integration: called from `t.c` after open/create and `timestamp_init`. It depends on timestamp configuration, global RNG `g.extra_rnd`, tracing, and mirror verification from `verify.c`. It protects correctness for `preserve_prepared` and precise checkpoint configurations.

Risks and test signals: timestamp selection must remain greater than prepare timestamps; incorrect claim strings or timestamp ordering can panic prepared transaction resolution. `WT_NOTFOUND` is expected only for no cursor/open exhaustion. Useful signals are trace messages for discovered and claimed prepared ids, checkpoint success, and mirror verification failures after the resolution checkpoint.
