# sources/test-tools/syzkaller/syz-cluster/pkg/db/base_finding_repo.go

## Purpose
Repository for BaseFindings with exact/date-window existence checks.

## Important APIs, Types, and Functions
BaseFindingRepository, Save, Exists.

## Control Flow
Save upserts; Exists searches by config/arch/title and commit hash or seven-day commit-date span.

## State and Persistence
Persists BaseFindings in Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
