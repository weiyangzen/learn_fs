# sources/sync-backup/git-lfs/tq/ssh_test.go

Purpose: minimal SSH adapter startup error test.

Important APIs/types/functions: `TestSSHAdapterWorkerStartingNilTransfer`.

Control flow: constructs an `SSHAdapter` with nil transfer and asserts `WorkerStarting` returns an error mentioning the SSH transfer adapter.

State and persistence: none.

Dependencies and integration points: validates defensive behavior used before SSH worker goroutines process jobs.

Risks: does not cover SSH batch parsing or upload/download behavior.

Test signals: narrow but useful guard for nil dependency handling.
