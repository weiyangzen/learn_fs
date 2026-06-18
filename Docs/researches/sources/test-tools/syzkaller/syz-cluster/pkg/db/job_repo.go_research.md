# sources/test-tools/syzkaller/syz-cluster/pkg/db/job_repo.go

## Purpose
Repository for Jobs with ExtID duplicate prevention.

## Important APIs, Types, and Functions
JobRepository, Insert, ErrJobExists.

## Control Flow
Transactionally checks Jobs by ExtID, runs callback once, then inserts.

## State and Persistence
Persists Jobs; callback may set PatchURI.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
