# sources/storage-engines/tikv/tests/failpoints/cases/test_conf_change.rs

Purpose: exercises edge cases around peer removal, local reader cleanup, writes racing destruction, stale peer cache, redundant conf changes via snapshots, and apply FSM pending-state recovery.

Important APIs and functions: tests include `test_destroy_local_reader`, `test_write_after_destroy`, `test_tick_after_destroy`, `test_stale_peer_cache`, `test_redundant_conf_change_by_snapshot`, and `test_handle_conf_change_when_apply_fsm_resume_pending_state`.

Control flow: cluster setup adds/removes peers through PD, transfers leaders, installs packet filters, pauses apply or destroy failpoints, and checks engine visibility/region cleanup after resuming.

State and persistence: key state includes region local data removal, local reader delegates, peer cache contents, on-disk versus in-memory conf state after snapshot restore, and pending apply state during conf change.

Dependencies and integration: uses node/server clusters including v2 variants, PD client, raft message filters, conf-change admin requests, and lease-read helpers.

Risks and test signals: several tests rely on sleeps around async destroy/apply. Signals guard against stale local reads, writes landing on destroyed peers, and inconsistent membership state.
