# sources/storage-engines/tikv/tests/integrations/raftstore/mod.rs

Purpose: registers the raftstore integration-test suite. The modules cover bootstrap, stale data cleanup, compaction, configuration change, early apply recovery, flashback, hibernation, joint consensus, lease reads, snapshots, transport, replication modes, stale peers, status commands, unsafe recovery, and more.

Important APIs and declarations: a long list of `mod test_*;` declarations includes the files researched in this work item and additional raftstore coverage.

Control flow: there is no runtime body. Rust test discovery includes each declared module, and macro-generated tests in those modules instantiate node/server clusters across raftstore v1/v2 variants.

State and persistence: none in this module. Child tests create all RocksDB, raft engine, PD, failpoint, transport, and snapshot state.

Dependencies and integration points: acts as the root integration point for `test_raftstore`, `test_raftstore_v2`, raftstore core, PD mock clients, engines, and TiKV server components.

Risks: declaration order can matter for compile errors and module visibility diagnostics, though tests should be independent. Removing a module from this file removes its coverage from the integration test crate.

Test signals: successful compilation and test discovery of the raftstore subtree.
