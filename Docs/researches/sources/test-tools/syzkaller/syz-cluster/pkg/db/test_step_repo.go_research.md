# sources/test-tools/syzkaller/syz-cluster/pkg/db/test_step_repo.go

## Purpose
Repository for SessionTestSteps and base/patched grouping.

## Important APIs, Types, and Functions
SessionTestStepRepository, Store, ListForSession, GroupTestSteps, TestStepGroup.

## Control Flow
Store replaces a logical step by deleting old row and inserting new row; grouping aligns base/patched by title.

## State and Persistence
Persists SessionTestSteps.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
