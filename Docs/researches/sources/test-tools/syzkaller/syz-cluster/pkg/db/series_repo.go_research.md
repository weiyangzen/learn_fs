# sources/test-tools/syzkaller/syz-cluster/pkg/db/series_repo.go

## Purpose
Repository for series, patches, dashboard filters, search, and version history.

## Important APIs, Types, and Functions
SeriesRepository, Insert, GetByExtID, ListLatest, ListPreviousVersions, ListPatches, Count, PatchByID.

## Control Flow
Insert rejects duplicate ExtID and stores patches; ListLatest builds filters then enriches with latest sessions and finding counts.

## State and Persistence
Persists Series/Patches and reads Sessions/Findings/Stats.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
