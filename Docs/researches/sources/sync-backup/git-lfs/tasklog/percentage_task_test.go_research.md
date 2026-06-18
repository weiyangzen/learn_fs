<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/percentage_task_test.go -->
# sources/sync-backup/git-lfs/tasklog/percentage_task_test.go

Purpose: unit tests for `PercentageTask` progress calculation and completion semantics.

Important APIs/types/functions: tests `NewPercentageTask`, `Count`, `Complete`, `Updates`, and `Throttled`.

Control flow: verifies initial 0 percent update, incremental 30 percent formatting, 100 percent for zero totals, channel closure at total count or explicit complete, idempotent complete after natural closure, and panic on overcount.

State and persistence: in-memory channel and atomic counter only.

Dependencies and integration points: validates formatting consumed by `Logger` progress output.

Risks: exact spacing in percentage strings is asserted, so UI formatting changes require test updates.

Test signals: direct coverage for normal, zero-total, complete, throttled, and overcount paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/percentage_task_test.go -->
