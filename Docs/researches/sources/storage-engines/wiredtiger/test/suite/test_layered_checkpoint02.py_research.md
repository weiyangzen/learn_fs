# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint02.py

Purpose: tests follower visibility and cursor stability across layered-table checkpoints and leader/follower state changes in disaggregated storage.

Important APIs and functions: decorated with `@disagg_test_class`; scenarios use disaggregated-only storage. Helpers `put_data`, `check_data_follower`, `scan_data_follower`, `close_cursors`, `reset_cursors`, and `reset_follow_cursor` manage leader writes and follower reads. It uses `disagg_advance_checkpoint` and opens a separate follower connection with `disaggregated=(role="follower")`.

Control flow: the test creates layered tables on the leader, opens a follower, writes version 0 and checkpoints/advances follower, verifies. It writes version 1 and keeps follower cursors open, writes version 2 and reopens cursors, writes version 3 and resets cursors, then scans half of version 3 with open cursors, writes/checkpoints version 4 and advances follower, confirms the open layered cursors continue scanning old version 3, then closes/reopens and sees version 4. Later sections continue testing state changes such as follower step-up to leader and visibility of new data.

State and persistence behavior: checkpoint advancement changes the follower's visible state, but open cursor iteration should remain insulated from subsequent state changes. Closed/reset cursors should observe the appropriate latest checkpoint.

Dependencies and integration points: integrates disaggregated leader/follower roles, layered URIs, checkpoint propagation, cursor positioning, string key ordering, and non-layered disagg block-manager configuration paths.

Risks and edge cases: cursor ordering uses lexicographic sorted string keys (`keys_in_order`), not numeric order. Non-layered cursor handling has a source comment about reset/reopen behavior, so layered and non-layered URI expectations differ.

Test signals: follower reads exact value prefixes for each checkpoint version; open layered scans continue old values after checkpoint advancement; reopened scans see new values.
