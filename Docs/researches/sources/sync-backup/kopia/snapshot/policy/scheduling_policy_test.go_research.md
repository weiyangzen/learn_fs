# sources/sync-backup/kopia/snapshot/policy/scheduling_policy_test.go

Purpose: validates snapshot scheduling edge cases and time-of-day normalization.

Important APIs/types/functions: `TestNextSnapshotTime` and `TestSortAndDedupeTimesOfDay`. The schedule cases exercise `SchedulingPolicy.NextSnapshotTime` with interval seconds, time-of-day slices, cron strings, `RunMissed`, and `Manual`.

Control flow: each table row supplies `now`, `previousSnapshotTime`, policy, expected next time, and expected availability. Cases cover overdue intervals, future previous snapshots, mixed interval and time-of-day priority, tomorrow rollover, cron month/day rules, and missed-run immediate execution.

State and persistence: no persistent policy writes; all times use `time.Local` and fixed dates.

Dependencies and integration points: indirectly validates `cronexpr` interpretation and the scheduler behavior used by automatic snapshot runners.

Risks and test signals: time-zone dependence is constrained by constructing expected values in `time.Local`. Missing validation tests mean cron parsing errors and manual-combination validation are covered elsewhere or by callers. Signals are exact `time.Time` equality and boolean availability.
