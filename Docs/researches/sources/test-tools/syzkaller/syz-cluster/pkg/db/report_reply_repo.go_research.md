# sources/test-tools/syzkaller/syz-cluster/pkg/db/report_reply_repo.go

## Purpose
Repository for report reply records and parent lookup.

## Important APIs, Types, and Functions
ReportReplyRepository, FindParentReportID, Insert, ErrReportReplyExists.

## Control Flow
FindParentReportID joins replies to reports by reporter; Insert rejects duplicate report/message pairs.

## State and Persistence
Persists ReportReplies.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
