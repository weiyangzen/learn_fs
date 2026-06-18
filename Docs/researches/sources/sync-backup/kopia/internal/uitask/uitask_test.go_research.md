<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/uitask/uitask_test.go -->
# sources/sync-backup/kopia/internal/uitask/uitask_test.go

- Purpose: Tests UI task manager behavior, logging, counters, retention, summaries, and cancellation ordering.
- Important APIs/types/functions: `TestUITask_withoutPersistentLogging`, `TestUITask_withPersistentLogging`, `testUITaskInternal`, `verifyTaskList`, `TestUITaskCancel_NonExistent`, `TestUITaskCancel_AfterOnCancel`, `TestUITaskCancel_BeforeOnCancel`, `verifyTaskLog`, `logText`, `mustFindTask`.
- Control flow: Tests run tasks synchronously, inspect running/completed lists, emit logs, verify format-log filtering and max log retention, report counters/progress, force failures, age out finished tasks, and test cancellation before/after callback registration.
- State and persistence: Uses in-memory manager state and an optional external log buffer for persistent logging mode.
- Dependencies and integration points: Integrates `logging`, `content.FormatLogModule`, `google/uuid`, `cmp`, and `testify/require`.
- Risks and edge cases: Cancellation tests use real sleeps and goroutines; persistent logging assertion is exact text.
- Test signals: Direct high-coverage test suite for `uitask`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/uitask/uitask_test.go -->
