# sources/test-tools/syzkaller/syz-cluster/pkg/db/stats_repo.go

## Purpose
Dashboard/statistics aggregate query repository.

## Important APIs, Types, and Functions
StatsRepository and weekly/monthly count/status/delay/prevented-bug/job query methods.

## Control Flow
Runs Spanner SQL aggregations and post-computes finished status counts.

## State and Persistence
Read-only aggregate queries over Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
