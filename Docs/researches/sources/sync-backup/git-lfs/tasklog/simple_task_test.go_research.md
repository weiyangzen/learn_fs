<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/simple_task_test.go -->
# sources/sync-backup/git-lfs/tasklog/simple_task_test.go

Purpose: unit tests for `SimpleTask`.

Important APIs/types/functions: tests `NewSimpleTask`, `Log`, `Logf`, `Complete`, `OnComplete`, `Updates`, and `Throttled`.

Control flow: tests run a goroutine to drain updates and call `OnComplete`, then verify emitted strings and channel closure. A separate test checks `Throttled` is false.

State and persistence: in-memory channels/waitgroup only.

Dependencies and integration points: validates the handshake expected by `Logger.logTask`.

Risks: tests must call `OnComplete`; otherwise they would deadlock, mirroring the production contract.

Test signals: direct coverage for plain log, formatted log, complete/channel close, and throttling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/simple_task_test.go -->
