# sources/test-tools/syzkaller/syz-cluster/pkg/db/build_repo.go

## Purpose
Repository for Build rows and latest matching build lookup.

## Important APIs, Types, and Functions
BuildRepository, Insert, LastBuildParams, LastBuiltTree.

## Control Flow
Insert assigns UUID if missing; LastBuiltTree builds optional filters and orders by CommitDate DESC LIMIT 1.

## State and Persistence
Persists Builds in Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
