# sources/storage-engines/tikv/tests/failpoints/cases/test_cmd_epoch_checker.rs

Purpose: tests raft command proposal epoch checking and callback behavior across split, merge, rollback merge, leader transfer, conf change, partition, and delayed propose windows.

Important APIs and functions: `CbReceivers` asserts proposed/committed/applied callback states. `make_cb` builds callbacks with proposed and committed hooks. `make_write_req` creates a region-epoch write request for a key. Tests cover rejecting proposals during split/merge/rollback/leader-transfer, accepting during conf change, not invoking committed callback on failure to commit, and proposals delayed before transfer/split/merge.

Control flow: tests pause apply stages with failpoints such as `apply_before_split`, `apply_before_prepare_merge`, `apply_before_commit_merge`, `apply_before_rollback_merge`, and `force_delay_propose_batch_raft_command`; submit async commands directly to node routers; then resume operations and assert callback ordering and errors.

State and persistence: region epoch, merge state, split state, and raft commit/apply progression are central. KV reads verify successful applied commands.

Dependencies and integration: uses raftstore message APIs, `RocksSnapshot`, `block_on_timeout`, and `test_raftstore`.

Risks and test signals: callback timing can be delicate; the test intentionally covers alternate proposed-callback code paths. Signals prevent stale epoch proposals and incorrect callback invocation.
