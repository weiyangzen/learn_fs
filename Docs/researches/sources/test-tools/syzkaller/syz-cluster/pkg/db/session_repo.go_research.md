# sources/test-tools/syzkaller/syz-cluster/pkg/db/session_repo.go

## Purpose
Repository for sessions, lifecycle start, scheduling queues, and report-generation queue.

## Important APIs, Types, and Functions
SessionRepository, Start, Insert, ListRunning, ListWaiting, ListForSeries, MissingReportList.

## Control Flow
Start sets StartedAt and updates Series.LatestSessionID for non-job sessions; ListWaiting prioritizes job sessions.

## State and Persistence
Persists Sessions and mutates Series latest-session pointer.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
