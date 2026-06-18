# sources/storage-engines/tikv/tests/integrations/backup/disk_snap.rs

See the grouped report section in `Docs/researches/groups/subset-b-008947_research.md` for the full source-aligned research. Summary: this integration test verifies disk snapshot backup prepare guards split, conf change, transfer leader, and merge operations, aborts superseded prepare streams, and waits for apply before reporting backup readiness. It uses `test_backup::disk_snap::Suite`, prepare/finalize calls, raft command callbacks, region packet filters, and observable data checks after wait-apply.
