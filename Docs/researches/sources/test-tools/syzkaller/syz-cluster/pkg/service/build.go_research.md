# sources/test-tools/syzkaller/syz-cluster/pkg/service/build.go

## Purpose
Service wrapper for build upload and lookup.

## Important APIs, Types, and Functions
BuildService, NewBuildService, Upload, LastBuild, makeBuildInfo.

## Control Flow
Maps api.UploadBuildReq to db.Build, writes log/config blobs, inserts build, and maps latest build back to API.

## State and Persistence
Persists Builds in Spanner and log/config blobs in blob storage.

## Dependencies and Integration Points
Service layer integrates api contracts, db repositories, blob storage, URL generation, and controller/reporter handlers.

## Risks and Edge Cases
Risks include orphaned blobs after DB write failures, subtle dedup/grouping semantics, and caller-visible domain errors needing correct HTTP mapping.

## Test Signals
Covered by controller/reporter/retest integration tests plus db repository tests.
