# sources/storage-engines/tikv/tests/integrations/raftstore/test_early_apply.rs

Purpose: verifies TiKV can recover when apply state has advanced beyond raft log state after simulated raft engine data loss, including leader, follower, and all-node commit-index loss scenarios.

Important APIs and functions: `delete_old_data` scans raft entries, builds a `RaftLocalState` with the last index, and uses `RaftEngineDebug::clean` plus `consume` to remove old raft data. `DataLost` classifies which peers lose commit information. Generic `test` orchestrates packet filtering, action/check execution, raft engine snapshot/restore, node restart, and leader restoration. `test_early_apply` runs put, split, and remove-peer cases under the selected loss mode.

Control flow: a node cluster is configured to avoid automatic log compaction, transfer leadership based on loss mode, and write initial data. For each action, append responses are filtered so selected peers have mismatched raft/apply progress. The test captures raft engine data, verifies the action applied, stops selected nodes, deletes old raft data, restores captured batches, restarts nodes, and then requires the cluster to keep serving.

State and persistence: directly mutates raft engine persisted entries and local state. It validates engine key data, split metadata, remove-peer cleanup, raft local last indexes, and internal apply index used by raft election/campaign logic.

Dependencies and integration points: uses raftstore store helpers, `RaftEngineDebug`, raft message filters, callbacks, snapshot/request configuration, and cluster restart paths.

Risks: intentionally corrupting raft persistence is fragile and tightly coupled to raft engine cleanup semantics. Filtered append responses and asynchronous actions can be timing-sensitive. The all-lost case models severe crash recovery but cannot cover every production disk-loss pattern.

Test signals: after restart, puts and splits remain applied, removed peers are cleaned where expected, leaders can be transferred back, read requests succeed after re-commit, and a later write can commit after internal apply index repair.
