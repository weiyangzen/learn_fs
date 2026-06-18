# sources/test-tools/syzkaller/syz-cluster/pkg/db/base_finding_repo_test.go

## Purpose
Tests BaseFindingRepository matching semantics.

## Important APIs, Types, and Functions
TestBaseFindingRepository.

## Control Flow
Checks unknown title, exact match, close-date match, future-date rejection, and far-past rejection.

## State and Persistence
Uses transient Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
