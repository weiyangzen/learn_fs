<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/timetrack/estimator.go -->
# sources/sync-backup/kopia/internal/timetrack/estimator.go

- Purpose: Estimates task completion percentage, end time, remaining duration, and speed.
- Important APIs/types/functions: `Estimator`, `Timings`, `Estimate`, `Completed`, `Start`.
- Control flow: `Estimate` requires elapsed time over one second and positive progress/total, clamps completed ratio for prediction, computes remaining time against `clock.Now`, and returns speed. `Completed` returns elapsed duration and average speed.
- State and persistence: Holds only an in-memory start time.
- Dependencies and integration points: Uses `clock` and real `time.Now`.
- Risks and edge cases: ETA is unavailable for short or zero-progress tasks; percent uses raw completed/total and can exceed 100 even though prediction clamps.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/timetrack/estimator.go -->
