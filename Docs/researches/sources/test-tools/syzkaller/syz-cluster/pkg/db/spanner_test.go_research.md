# sources/test-tools/syzkaller/syz-cluster/pkg/db/spanner_test.go

## Purpose
Migration reversibility smoke test.

## Important APIs, Types, and Functions
TestMigrations.

## Control Flow
Runs all migrations down and back up on a transient DB.

## State and Persistence
Uses transient Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
