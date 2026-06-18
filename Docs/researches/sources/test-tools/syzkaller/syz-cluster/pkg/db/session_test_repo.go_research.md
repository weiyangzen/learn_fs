# sources/test-tools/syzkaller/syz-cluster/pkg/db/session_test_repo.go

## Purpose
Repository for SessionTests and build enrichment.

## Important APIs, Types, and Functions
SessionTestRepository, InsertOrUpdate, Get, BySession, BySessionRaw, FullSessionTest.

## Control Flow
Upserts tests by session/name; BySession loads referenced base/patched builds and attaches pointers.

## State and Persistence
Persists SessionTests and reads Builds.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
