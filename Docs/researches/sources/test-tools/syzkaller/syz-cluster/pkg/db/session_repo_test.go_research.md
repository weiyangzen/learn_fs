# sources/test-tools/syzkaller/syz-cluster/pkg/db/session_repo_test.go

## Purpose
Tests session lifecycle and queue behavior.

## Important APIs, Types, and Functions
Tests latest-session update, FIFO waiting order, job priority, and job sessions not updating latest session.

## Control Flow
Creates series/sessions/jobs/reports and calls repository methods.

## State and Persistence
Uses transient Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
