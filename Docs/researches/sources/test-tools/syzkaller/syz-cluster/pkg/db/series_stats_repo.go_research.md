# sources/test-tools/syzkaller/syz-cluster/pkg/db/series_stats_repo.go

## Purpose
Repository for series statistics refresh selection and bulk update.

## Important APIs, Types, and Functions
SeriesStatsRepository, ListOutdated, BulkUpdate, ListOutdatedFilter.

## Control Flow
Lists finished latest-session series missing/current-version stats; bulk updates existing stats rows.

## State and Persistence
Persists SeriesStats.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
