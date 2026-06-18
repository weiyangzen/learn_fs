<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/rate_estimator.go -->
# sources/sync-backup/restic/internal/ui/backup/rate_estimator.go

## Purpose
Estimates recent backup throughput for remaining-time calculation.

## Important APIs and Control Flow
`rateEstimator` uses a ring/bucket model over time; `newRateEstimator`, `recordBytes`, `rate`, and bucket-width logic track bytes over recent intervals. Control flow advances buckets as time moves forward, adds completed bytes to the current bucket, and computes a bytes-per-second rate over populated buckets.

## State, Persistence, Dependencies, and Integration
State is in-memory time buckets and last-update timestamps. Integration is with `backup.Progress` after scan completion.

## Risks and Test Signals
Risks are responsiveness versus stability tradeoffs and edge cases at bucket boundaries. Tests cover default rate, simple rates, bucket width, and responsiveness to changing throughput.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/rate_estimator.go -->
