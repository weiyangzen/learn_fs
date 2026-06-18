# sources/test-tools/syzkaller/syz-cluster/pkg/service/base_finding.go

## Purpose
Service wrapper for base-kernel finding upload/status checks.

## Important APIs, Types, and Functions
BaseFindingService, NewBaseFindingService, ErrBuildNotFound, Upload, Status, makeBaseFinding.

## Control Flow
Resolves BuildID to commit/config/arch/date and saves or queries BaseFindingRepository.

## State and Persistence
Reads Builds and writes/reads BaseFindings in Spanner.

## Dependencies and Integration Points
Service layer integrates api contracts, db repositories, blob storage, URL generation, and controller/reporter handlers.

## Risks and Edge Cases
Risks include orphaned blobs after DB write failures, subtle dedup/grouping semantics, and caller-visible domain errors needing correct HTTP mapping.

## Test Signals
Covered by controller/reporter/retest integration tests plus db repository tests.
