# sources/test-tools/syzkaller/syz-cluster/pkg/db/util_test.go

## Purpose
Shared db test fixture helpers.

## Important APIs, Types, and Functions
dummyTestData and helpers for series/session/test/report/finding lifecycle.

## Control Flow
Directly creates and mutates repository rows while asserting success.

## State and Persistence
Creates transient Spanner fixture state.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
