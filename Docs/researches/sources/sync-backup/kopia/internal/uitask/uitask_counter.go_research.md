<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/uitask/uitask_counter.go -->
# sources/sync-backup/kopia/internal/uitask/uitask_counter.go

- Purpose: Defines JSON counter values and constructors for UI task counters with units/severity levels.
- Important APIs/types/functions: `CounterValue`, `BytesCounter`, `SimpleCounter`, `NoticeBytesCounter`, `NoticeCounter`, `WarningBytesCounter`, `WarningCounter`, `ErrorBytesCounter`, `ErrorCounter`.
- Control flow: Constructors return small value structs with optional `bytes` units and level strings.
- State and persistence: No state; values are embedded into task API responses.
- Dependencies and integration points: Used by upload/progress reporters and UI task JSON output.
- Risks and edge cases: Level strings are an implicit UI contract.
- Test signals: `uitask_test.go` asserts constructor output through reported counters.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/uitask/uitask_counter.go -->
