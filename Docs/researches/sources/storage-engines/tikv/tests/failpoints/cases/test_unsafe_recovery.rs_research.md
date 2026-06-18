# sources/storage-engines/tikv/tests/failpoints/cases/test_unsafe_recovery.rs

See the grouped report section in `Docs/researches/groups/subset-b-008947_research.md` for the full source-aligned research. Summary: this file tests unsafe recovery when quorum is lost, entries or snapshots are unapplied, recovery plans are resent or timed out, merges are rolled back, and apply-before-persist creates divergent raft persistence. It drives PD `RecoveryPlan`s, force-leader mode, demotion/create reports, raft/apply state reads, and final data checks after recovery.
