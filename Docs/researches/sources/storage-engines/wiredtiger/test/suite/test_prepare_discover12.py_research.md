# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover12.py

Purpose: validates that a prepared insert rolled back on a follower stays absent after step-up and checkpoints, including when a newer regular commit on the same key is written before step-up.

Important APIs and types: helper methods `_open_follower`, `_checkpoint`, `_evict_key`, `_create_leader_baseline`, `_prepare_then_rollback`, `_commit_value`, `_set_stable_and_checkpoint`, `_assert_search`, `wiredtiger.WT_NOTFOUND`, and disaggregated role reconfiguration.

Control flow: each test creates a leader baseline key, checkpoints, closes, opens a follower, performs and rolls back a prepared insert at key 1, then steps up to leader. One path only checks the rolled-back insert; the other also commits a newer value at timestamp 150. Both paths checkpoint at stable timestamps around the rollback/newer commit, evict the key, advance stable, and assert reads.

State and persistence behavior: rollback timestamps must be reflected in persisted key state. After rollback, key 1 is absent until any newer committed value becomes visible, while the unrelated baseline key remains intact.

Dependencies and integration points: follower-side prepared rollback, stable checkpoint durability, eviction/reload, disaggregated step-up, and timestamp visibility.

Risks: same-key rollback plus newer commit is a high-risk update-chain ordering case. Eviction ensures the test covers disk state, not only memory.

Test signals: key 1 is `WT_NOTFOUND` after rollback-only flow; in the newer-commit flow it is absent at timestamp 120 and has `newer_committed_value` at timestamp 160.
