# sources/test-tools/syzkaller/syz-cluster/pkg/db/series_repo_test.go

## Purpose
Broad tests for series repository behavior.

## Important APIs, Types, and Functions
Tests get/list/search/update/previous versions.

## Control Flow
Exercises ordering, cc/status/finding filters, SEARCH queries, invalidated findings, and updates.

## State and Persistence
Uses transient Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
