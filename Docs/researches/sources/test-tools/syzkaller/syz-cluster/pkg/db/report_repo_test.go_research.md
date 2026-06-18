# sources/test-tools/syzkaller/syz-cluster/pkg/db/report_repo_test.go

## Purpose
Tests report repository and missing-report queue behavior.

## Important APIs, Types, and Functions
TestReportRepository and TestSessionsWithoutReports.

## Control Flow
Checks unsent counts and finished sessions with findings/no report selection.

## State and Persistence
Uses transient Spanner across reports/sessions/findings.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
