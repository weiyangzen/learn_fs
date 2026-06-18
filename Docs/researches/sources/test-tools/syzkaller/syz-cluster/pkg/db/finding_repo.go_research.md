# sources/test-tools/syzkaller/syz-cluster/pkg/db/finding_repo.go

## Purpose
Repository for logical finding replacement and listing.

## Important APIs, Types, and Functions
FindingRepository, FindingID, Store, mustStore, ListForSession.

## Control Flow
Store loads old finding/session in a transaction, calls callback, deletes old row, and inserts replacement.

## State and Persistence
Persists Findings with blob URI fields.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
