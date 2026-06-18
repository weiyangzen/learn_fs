# sources/storage-engines/tikv/tests/failpoints/cases/test_early_apply.rs

Purpose: validates early-apply restrictions and correctness around unpersisted logs, merge catch-up, and leader demotion with overlapping entry cache contents.

Important APIs and functions: tests include singleton no-early-apply, multi-region early apply, yield followed by many entries, and leader demote by append. Uses failpoints `raft_before_save_on_store_1`, `before_handle_normal_3`, `after_handle_catch_up_logs_for_merge_1003`, and `pause_on_peer_collect_message`.

Control flow: tests pause raft persistence or apply handling, issue writes across singleton/multi-peer regions, merge regions with large entries, restart clusters, and inject modified `MsgAppend` messages directly through `PeerMsg`.

State and persistence: distinguishes committed, applied, and persisted logs. It validates KV visibility before/after persist and restart, and entry cache consistency under demotion.

Dependencies and integration: uses node clusters plus v2 variants, raft message filters, PD merges, and `block_on_timeout`.

Risks and test signals: direct message mutation is artificial but targets a documented corner case. Signals protect against applying singleton unpersisted logs, restart inconsistency, and entry cache panics.
