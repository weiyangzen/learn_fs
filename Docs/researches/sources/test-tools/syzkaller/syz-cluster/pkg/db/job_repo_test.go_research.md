# sources/test-tools/syzkaller/syz-cluster/pkg/db/job_repo_test.go

## Purpose
Tests JobRepository duplicate ExtID behavior.

## Important APIs, Types, and Functions
TestJobRepo.

## Control Flow
Inserts one job and expects ErrJobExists for same ExtID.

## State and Persistence
Uses transient Spanner plus prerequisite report/session.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
