# sources/storage-engines/tikv/tests/failpoints/cases/test_hibernate.rs

Purpose: tests raftstore hibernation behavior around restart, busy-on-apply, unstable entry buffers, forced wakeup, store disconnect, and long-uncommitted proposal ticks.

Important APIs and functions: tests include `test_break_leadership_on_restart`, `test_restart_peer_busy_on_apply`, `test_hibernate_region_releases_unstable_entry_buffer`, `test_forcely_awaken_hibenrate_regions`, `test_store_disconnect_with_hibernate`, and `test_check_long_uncommitted_proposals_while_hibernate`. They use `GroupState`, `PeerTick`, `ExtraMessageType`, store heartbeats, and failpoints around raft ticks/apply checks.

Control flow: each test configures short raft ticks, enables hibernate, waits for idle state, injects messages or node restarts, then checks election suppression, busy flags, buffer release, wakeup callbacks, or tick suppression/resumption.

State and persistence: raft group hibernate state, unstable entry buffers, leader committed index, store stats `is_busy`, and KV replication are core state.

Dependencies and integration: uses node/server clusters, PD client, raft message filters, and `ReadableDuration`.

Risks and test signals: timing-heavy by design. Signals prevent false elections after restart, stuck busy state, memory retention after hibernation, and missed wakeups.
