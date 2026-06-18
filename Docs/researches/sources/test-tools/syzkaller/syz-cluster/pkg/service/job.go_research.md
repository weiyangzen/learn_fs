# sources/test-tools/syzkaller/syz-cluster/pkg/service/job.go

## Purpose
Service for user-submitted patch-test jobs.

## Important APIs, Types, and Functions
JobService, NewJobService, GetJob, getFindingGroups, SubmitJob, JobLink, ErrPatchTooLarge.

## Control Flow
Validates report/session, stores bounded patch data, inserts Job, creates job-linked Session, and groups original findings by patched build for retest tasks.

## State and Persistence
Persists Jobs and job Sessions; stores patch blobs externally.

## Dependencies and Integration Points
Service layer integrates api contracts, db repositories, blob storage, URL generation, and controller/reporter handlers.

## Risks and Edge Cases
Risks include orphaned blobs after DB write failures, subtle dedup/grouping semantics, and caller-visible domain errors needing correct HTTP mapping.

## Test Signals
Covered by controller/reporter/retest integration tests plus db repository tests.
