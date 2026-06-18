# sources/sync-backup/kopia/snapshot/policy/scheduling_policy.go

Purpose: defines automatic snapshot scheduling policy, including fixed intervals, local times of day, cron expressions, missed-run handling, and manual-only snapshots.

Important APIs/types/functions: `TimeOfDay.Parse`, `TimeOfDay.String`, `SortAndDedupeTimesOfDay`, `SchedulingPolicy`, `Interval`, `SetInterval`, `NextSnapshotTime`, `getNextTimeOfDaySnapshot`, `getNextCronSnapshot`, `checkMissedSnapshot`, `Merge`, `IsManualSnapshot`, `SetManual`, `ValidateSchedulingPolicy`, and `stripCronComment`.

Control flow: `NextSnapshotTime` exits for manual policies, computes interval, time-of-day, and cron candidates in local time, chooses the earliest, then may return `now` when `RunMissed` is enabled and the next regular run is more than 30 minutes away. Merge appends parent times unless `NoParentTimesOfDay` blocks it.

State and persistence: `SetManual` loads or creates a defined repository policy for a source and saves `Manual=true`; other scheduling operations are in-memory.

Dependencies and integration points: uses `hashicorp/cronexpr`, repository policy APIs, `snapshot.SourceInfo`, and policy tree consumers.

Risks and test signals: invalid cron is ignored during scheduling but rejected by validation; manual cannot combine with other fields. Tests cover intervals, cron, time-of-day, missed runs, and dedupe.
