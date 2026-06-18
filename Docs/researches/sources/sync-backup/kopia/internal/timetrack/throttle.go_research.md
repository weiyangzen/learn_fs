<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/timetrack/throttle.go -->
# sources/sync-backup/kopia/internal/timetrack/throttle.go

- Purpose: Provides atomic throttling for periodic UI/progress output.
- Important APIs/types/functions: `Throttle`, `ShouldOutput`, `Reset`.
- Control flow: `ShouldOutput` reads the next allowed Unix nano timestamp, compares real time, and uses compare-and-swap to reserve the next interval; `Reset` clears the timestamp.
- State and persistence: In-memory atomic int64 only.
- Dependencies and integration points: Used by progress reporters that need cheap concurrent throttling.
- Risks and edge cases: Uses wall-clock time, so clock jumps can affect throttling.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/timetrack/throttle.go -->
