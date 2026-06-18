<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/rate_estimator_test.go -->
# sources/sync-backup/restic/internal/ui/backup/rate_estimator_test.go

## Purpose
Tests backup throughput estimation behavior.

## Important APIs and Control Flow
The suite defines approximate float comparison and chunk application helpers. Tests cover zero/default rates, simple byte/time examples, bucket-width selection, and estimator responsiveness across bursts and idle periods. Control flow advances synthetic timestamps and records byte chunks into an estimator.

## State, Persistence, Dependencies, and Integration
State is deterministic test time and estimator buckets. Dependencies are standard time/testing only.

## Risks and Test Signals
The tests provide strong deterministic coverage for rate math, but real-world timing jitter is only indirectly represented.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/rate_estimator_test.go -->
