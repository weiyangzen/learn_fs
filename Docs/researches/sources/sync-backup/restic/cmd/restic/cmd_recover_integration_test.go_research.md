# sources/sync-backup/restic/cmd/restic/cmd_recover_integration_test.go

Purpose: integration test for recovering a forgotten snapshot's root tree.

Important APIs/types/functions: `testRunRecover`; `TestRecover`.

Control flow and state: the test creates backup data, backs it up, loads the snapshot metadata, forgets the snapshot, verifies snapshot list is empty, runs recover, verifies one snapshot exists, runs check, and cats the recovered snapshot path to the original tree ID.

Dependencies and integration points: uses backup/forget/list/check/cat helpers and the shared test environment. It disables the default list-once backend hook because recover/list operations may enumerate index files repeatedly.

Risks: focuses on forgotten snapshot recovery, not partially corrupt tree cases. Success depends on unpruned tree data remaining in packs.

Test signals: proves recover can create a new snapshot exposing the original forgotten root tree.
