# sources/sync-backup/kopia/tests/end_to_end_test/norace_test.go

## Purpose
Resource-heavy non-race test that long snapshot checkpointing does not leave incomplete checkpoint manifests after a successful final snapshot.

## Important APIs, Types, and Functions
Build-tagged `!race`. `TestSnapshotNoLeftoverCheckpoints` and helper `writeRandomFile`.

## Control Flow
The test writes a deterministic 1 GiB file, snapshots it with `--checkpoint-interval 1s`, verifies elapsed time exceeded the interval, then lists snapshots with `--incomplete` and asserts only one complete snapshot remains for the source.

## State and Persistence Behavior
Creates a large source file and checkpoint/final snapshot state in a real repository. Successful upload should clean up or hide incomplete checkpoints.

## Dependencies and Integration Points
Exercises upload checkpointing, snapshot list incomplete filtering, large file upload, and CLI command parsing through `clitestutil`.

## Risks
Very expensive in time/disk and excluded under race. It relies on the upload taking more than one second; slow or fast environments can affect timing assumptions.

## Test Signals
Confirms checkpoint generation during long uploads does not leave visible incomplete snapshots after completion.
