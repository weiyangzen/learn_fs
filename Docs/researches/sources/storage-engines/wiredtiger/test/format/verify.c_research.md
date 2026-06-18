# sources/storage-engines/wiredtiger/test/format/verify.c

Purpose: verifies table integrity with WiredTiger verify and checks mirrored tables contain equivalent original key/value data, including live, checkpoint, and mirrored-truncate-specific ranges.

Important APIs and functions: `table_verify`, `wts_verify`, `wts_verify_mirrors`, `wts_verify_mirrored_truncate`, and static mirror helpers `table_mirror_row_next`, `position_cursor_before`, `table_verify_mirror`, and failure reporting/page dump functions.

Control flow: `wts_verify` checkpoints, applies strict verify to each table, then optionally verifies mirrors unless salvage/reopen makes mirror comparison invalid. `table_verify_mirror` opens base and target cursors, retries checkpoint cursor open until checkpoint ids match, pins a live snapshot when not using checkpoint cursors, positions to a requested range for truncate checks, walks original records, compares key numbers and values, dumps diagnostic pages on first mismatch, and asserts no failures.

State and persistence: mostly read-only but creates checkpoints before verify and diagnostic page dumps on mismatch. It uses live snapshots or named checkpoint state and may preserve disaggregated layered components on first mismatch.

Dependencies and integration: invoked by `t.c`, `format_prepare_discover.c`, salvage, and `ops.c` mirrored truncates. It depends on `key_gen`, `atou32`, cursor wrappers, table metadata, trace flags, disagg settings, and WiredTiger strict verify.

Risks and test signals: mirror checks intentionally skip row-store inserted non-original keys and stop when both sides pass original rows. Live verification requires a pinned cursor to avoid snapshot refresh. Signals include strict verify errors, EBUSY warnings after retry, mirror mismatch messages, `FAIL.pagedump` diagnostics, and disagg preservation artifacts.
