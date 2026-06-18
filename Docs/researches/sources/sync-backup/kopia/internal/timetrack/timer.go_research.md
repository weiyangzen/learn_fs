<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/timetrack/timer.go -->
# sources/sync-backup/kopia/internal/timetrack/timer.go

- Purpose: Measures elapsed time from construction.
- Important APIs/types/functions: `Timer`, `Elapsed`, `StartTimer`.
- Control flow: `StartTimer` captures `time.Now`; `Elapsed` returns `time.Since(startTime)`.
- State and persistence: In-memory start timestamp only.
- Dependencies and integration points: Used by operations needing simple duration measurement.
- Risks and edge cases: Uses real time rather than injectable clock.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/timetrack/timer.go -->
