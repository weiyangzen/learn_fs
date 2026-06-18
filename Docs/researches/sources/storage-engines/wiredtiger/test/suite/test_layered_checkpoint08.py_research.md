# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint08.py

Purpose: tests dropping an empty layered table while a slow checkpoint is active, including the case where sweep has closed the idle data handle.

Important APIs/types/functions: extends `checkpoint_util`; uses `file_manager` close settings, `timing_stress_for_test=[checkpoint_slow]`, connection statistics `wiredtiger.stat.conn.dh_sweep_dead_close`, `wtthread.Thread`, `session.drop(..., checkpoint_wait=false)`, and follower `disagg_advance_checkpoint`.

Control flow: the test steps up to leader, sets stable timestamp, creates an empty table in a second session, waits for sweep to close the idle handle by polling stats, then starts a slow checkpoint in a thread. After checkpoint start it drops the table without waiting for checkpoint, joins the checkpoint, disables stress, opens a follower, advances it, and verifies the table still exists and is empty at the checkpoint being picked up. It then performs another leader checkpoint, advances the follower again, and verifies the table can no longer be opened.

State and persistence behavior: table metadata must remain visible to the checkpoint that began before the drop, then disappear after a later checkpoint. The sweep-closed handle ensures the path works without an open local handle.

Dependencies/integration points: data handle sweep, checkpoint/drop synchronization, disaggregated metadata, follower pickup, and checkpoint visibility rules.

Risks: polling sweep progress is inherently timing-dependent, though bounded by 60 seconds. The final open failure checks the leader session rather than follower session, so the key signal is metadata transition after later checkpoint.

Test signals: pass indicates concurrent drop does not corrupt the active checkpoint and later checkpoint correctly removes the object.
