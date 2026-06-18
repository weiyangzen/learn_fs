# sources/test-tools/syzkaller/syz-cluster/pkg/service/discussion.go

## Purpose
Service for recording email replies and identifying the original report.

## Important APIs, Types, and Functions
DiscussionService, NewDiscussionService, RecordReply, identifyReport.

## Control Flow
Identifies a report by explicit ReportID or root message ID/reporter, then inserts a ReportReply and handles duplicates idempotently.

## State and Persistence
Persists ReportReplies and reads SessionReports.

## Dependencies and Integration Points
Service layer integrates api contracts, db repositories, blob storage, URL generation, and controller/reporter handlers.

## Risks and Edge Cases
Risks include orphaned blobs after DB write failures, subtle dedup/grouping semantics, and caller-visible domain errors needing correct HTTP mapping.

## Test Signals
Covered by controller/reporter/retest integration tests plus db repository tests.
