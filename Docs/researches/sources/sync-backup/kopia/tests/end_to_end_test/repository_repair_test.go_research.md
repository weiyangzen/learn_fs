# sources/sync-backup/kopia/tests/end_to_end_test/repository_repair_test.go

## Purpose
Format-specific test for recovering a missing repository format blob.

## Important APIs, Types, and Functions
`formatSpecificTestSuite.TestRepositoryRepair`.

## Control Flow
The test creates a repo, writes several snapshots, deletes `kopia.repository` via blob command, disconnects, verifies reconnect fails, and for format v1 runs `repo repair filesystem` then verifies reconnect succeeds.

## State and Persistence Behavior
Deletes critical repository format state and relies on v1 embedded replicas in pack blobs for repair. Newer formats with password change enabled do not embed replicas, so repair is not expected there.

## Dependencies and Integration Points
Exercises blob removal, repo connect failure paths, repository repair command, format-version conditional behavior, and snapshot-generated pack blobs.

## Risks
Only v1 repair success is asserted; newer formats only assert failure before repair. Behavior is tightly coupled to format-blob replica policy.

## Test Signals
Confirms missing format blob prevents connect and v1 repair can reconstruct enough state to reconnect.
