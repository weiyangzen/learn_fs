<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower11.py

Purpose: ensures user tombstones in a follower ingest table are not removed until they are included in a checkpoint.

Important APIs/types/functions: uses separate leader and follower connections, timestamped `leader_put_data`, `checkpoint`, `create_follower`, `debug=(release_evict_page=true)` eviction sessions, `cursor.remove`, and `session.truncate`.

Control flow: both tests create a layered table, write leader data, checkpoint, and advance follower. `test_remove` removes every key on the follower with increasing commit timestamps, makes deletes globally visible on the follower, forces eviction over all deleted keys, and confirms they stay invisible. `test_truncate` performs a follower truncate from the first key to the end, advances stable/oldest, forces eviction, and similarly verifies all keys remain not found.

State and persistence behavior: globally visible user deletes/truncates in ingest must continue to protect visibility until checkpoint machinery has made them durable in the stable component.

Dependencies/integration points: integrates user tombstones, follower stable timestamps, eviction, and checkpoint pickup state. Risks include cursor reuse after eviction and timestamp counter assumptions. Test signals are WT_NOTFOUND during eviction and under timestamped verification.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower11.py -->
