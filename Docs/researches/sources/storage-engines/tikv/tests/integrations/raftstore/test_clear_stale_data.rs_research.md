# sources/storage-engines/tikv/tests/integrations/raftstore/test_clear_stale_data.rs

Purpose: verifies stale peer data is physically removed from RocksDB when a node restarts after some regions have been removed from that store.

Important APIs and functions: `init_db_with_sst_files` writes one key per SST in `CF_DEFAULT` and `CF_LOCK`, flushes, and compacts files into a target level. `check_db_files_at_level` reads RocksDB `num-files-at-levelN` properties. `check_kv_in_all_cfs` validates key presence across default/lock CFs. `test_clear_stale_data` performs region splits, peer removals, restart, and assertions.

Control flow: the test disables level-0 compaction triggers, starts a three-node server cluster, splits the keyspace into six regions, manufactures level-6 SST files, removes peers for odd regions from a selected node through PD, restarts that node, and checks that odd-region keys and half the SST files are gone.

State and persistence: manipulates RocksDB SST layout directly and verifies both logical key deletion and physical file-count reduction. Peer state changes are persisted by raftstore and observed after node restart.

Dependencies and integration points: uses `engine_rocks`, `engine_traits` CF APIs, RocksDB raw compaction options/properties, PD peer removal, raftstore split/restart behavior, and test cluster engines.

Risks: file-count assertions are sensitive to RocksDB compaction behavior and configuration. The test disables compaction to stabilize layout, but engine version changes could alter property semantics. It covers default and lock CFs but not write/raft CF payload removal.

Test signals: keys for retained even regions remain present in both CFs, odd-region keys are absent, and level-6 file count drops from six to three in each checked CF after restart.
