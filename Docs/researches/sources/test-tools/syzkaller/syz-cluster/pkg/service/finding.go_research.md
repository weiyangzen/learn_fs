# sources/test-tools/syzkaller/syz-cluster/pkg/service/finding.go

## Purpose
Service for finding save/list/get/invalidate/previous-version logic.

## Important APIs, Types, and Functions
FindingService, Save, saveAssets, InvalidateSession, List, ListPreviousFindings, Get, matchesPrevFindingsReq, deduplicateFindings, isBetterFinding.

## Control Flow
Saves blob assets, transactionally replaces logical findings, maps DB rows to public api.Finding, reads raw blobs back, and deduplicates reports by title.

## State and Persistence
Persists Findings and blob URIs; invalidation stamps InvalidatedAt.

## Dependencies and Integration Points
Service layer integrates api contracts, db repositories, blob storage, URL generation, and controller/reporter handlers.

## Risks and Edge Cases
Risks include orphaned blobs after DB write failures, subtle dedup/grouping semantics, and caller-visible domain errors needing correct HTTP mapping.

## Test Signals
Covered by controller/reporter/retest integration tests plus db repository tests.
