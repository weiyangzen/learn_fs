# sources/test-tools/syzkaller/syz-cluster/pkg/db/finding_repo_test.go

## Purpose
Tests finding insertion uniqueness and list ordering.

## Important APIs, Types, and Functions
TestFindingRepo.

## Control Flow
Creates tests/findings, asserts duplicate errors through mustStore, and verifies ordered list output.

## State and Persistence
Uses transient Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
