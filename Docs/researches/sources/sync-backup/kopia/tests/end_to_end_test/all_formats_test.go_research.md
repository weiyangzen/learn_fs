# sources/sync-backup/kopia/tests/end_to_end_test/all_formats_test.go

## Purpose
Smoke-tests repository creation, snapshotting, disconnect/reconnect, and snapshot listing across all supported encryption and hashing algorithms.

## Important APIs, Types, and Functions
`TestAllFormatsSmokeTest` iterates `encryption.SupportedAlgorithms(false)` and `hashing.SupportedAlgorithms()`, using `testdirtree.CreateDirectoryTree`, `repo create filesystem --block-hash --encryption`, `snap create`, and `clitestutil.ListSnapshotsAndExpectSuccess`.

## Control Flow
A shared small source tree is created once. Each encryption/hash subtest runs in parallel with a fresh CLI test repository, creates a snapshot, validates one source, reconnects, and validates the same source count again.

## State and Persistence Behavior
Creates many real filesystem repositories and one shared source tree. Repository format is not constrained beyond the algorithm flags.

## Dependencies and Integration Points
Exercises format initialization, cryptographic algorithm selection, content hashing, snapshot upload, and persisted config reconnect.

## Risks
The nested parallel matrix can be expensive. The test checks only basic usability, not restore correctness or algorithm-specific metadata.

## Test Signals
Failure indicates an algorithm combination cannot create, write, reconnect, or list snapshots.
