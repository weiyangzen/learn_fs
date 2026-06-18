# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover11.py

Purpose: verifies that a follower-claimed prepared transaction committed before step-up remains readable after stable timestamp advancement, eviction, and follower step-up to leader.

Important APIs and types: helper methods `_open_follower` and `_checkpoint`, `prepared_discover:`, `claim_prepared_id`, `timestamp_transaction`, `release_evict_page`, disaggregated role reconfigure, and timestamped reads.

Control flow: leader commits keys 1-3, prepares keys 4-6 with id 99999, checkpoints, rolls back locally, and closes. The follower opens from checkpoint metadata, discovers id 99999, claims and commits it at timestamp 200, advances stable to 250, forces eviction of keys 4-6, steps up to leader, checkpoints, and validates reads at timestamps 60 and 220.

State and persistence behavior: the committed prepared updates must survive eviction from follower memory and be properly drained during role step-up. They are invisible before the prepare/commit timeline and visible after commit timestamp.

Dependencies and integration points: prepared discovery, follower ownership of claim, stable timestamp advancement, eviction, disaggregated step-up drain, and layered table read paths.

Risks: bugs here can be masked if pages remain in memory; the explicit eviction is essential because it forces disk/restoration behavior.

Test signals: exactly `[99999]` is discovered; keys 4-6 are not found at timestamp 60 and equal prepared values at timestamp 220 after step-up.
