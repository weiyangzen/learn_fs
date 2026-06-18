# sources/storage-engines/tikv/tests/failpoints/cases/test_disk_snap_br.rs

Purpose: ignored regression test for backup disk snapshot behavior during region merge scheduling.

Important APIs and functions: `test_merge` uses `test_backup::disk_snap::Suite`, `assert_success`, `prepare_backup`, `wait_apply`, and failpoint `on_schedule_merge`.

Control flow: split a region, pause merge scheduling, issue merge, prepare backup, resume scheduling, manually advance source epoch to simulate prepare merge application, wait for backup apply awareness, then assert eventual merge.

State and persistence: region epochs and backup rejector state are central. It models a merge command interaction with backup prepare state.

Dependencies and integration: depends on backup disk-snapshot test harness and raftstore merge operations.

Risks and test signals: marked ignored with comment explaining current behavior intentionally does not reject `CommitMerge`, so this is documentation/regression scaffolding rather than active CI signal.
