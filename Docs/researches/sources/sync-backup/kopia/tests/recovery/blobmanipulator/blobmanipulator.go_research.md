
# sources/sync-backup/kopia/tests/recovery/blobmanipulator/blobmanipulator.go

## Purpose
Provides a recovery-test helper for creating repositories, generating random data, deleting/corrupting blobs, restoring snapshots, running maintenance, and invoking `snapshot fix` commands.

## Important APIs, Types, And Functions
- `BlobManipulator` holds a `kopiarunner.KopiaSnapshotter`, `snapmeta.KopiaSnapshotter`, optional `fiofilewriter.FileWriter`, repo path, maintenance flag, and current snapshot path.
- `NewBlobManipulator` creates command runner and metadata snapshotter; `getSnapshotter` skips/returns nil when `KOPIA_EXE` is missing.
- `ConnectOrCreateRepo`, `TakeSnapshot`, `DeleteSnapshot`, `VerifySnapshot`, and `RunMaintenance` wrap Kopia CLI operations.
- `DeleteBlob` and `getBlobIDRand` delete a named or first pack (`p`) blob.
- `writeRandomFiles`, `SetUpSystemUnderTest`, `SetUpSystemWithOneSnapshot`, and `GenerateRandomFiles` create test data via FIO.
- `RestoreGivenOrRandomSnapshot` restores a provided or random snapshot ID and returns stderr text on error for later parsing.
- `SnapshotFixRemoveFilesByBlobID`, `SnapshotFixRemoveFilesByFilename`, and `SnapshotFixInvalidFiles` invoke repair commands with `--commit`.

## Control Flow
Recovery tests instantiate `BlobManipulator`, set `DataRepoPath`, generate files/snapshots, optionally delete blobs or snapshots, run maintenance, attempt restores, parse failures, and run fix commands. Blob selection lists repository blobs in JSON and selects the first pack blob.

## State And Persistence Behavior
Creates and mutates filesystem Kopia repositories, writes random file trees through FIO, stores snapshots, deletes snapshots/blobs, and runs full maintenance with `--safety none`. `PathToTakeSnapshot` tracks the current FIO data directory for later snapshot calls.

## Dependencies And Integration Points
Uses `tests/robustness` interfaces, `fiofilewriter`, `snapmeta`, `kopiarunner`, `tests/tools/fio`, `repo/blob.Metadata`, and `snapshot.Manifest`.

## Risks And Edge Cases
`ConnectOrCreateRepo(dataRepoPath string)` ignores its parameter and uses `bm.DataRepoPath`, so callers must set the struct field correctly. `NewBlobManipulator` can return `(nil, nil)` when the snapshotter is unavailable; callers must handle nil. Random snapshot selection assumes non-empty snapshot lists. Blob deletion assumes a pack blob exists.

## Test Signals
Enables corruption/recovery tests with realistic CLI and repository operations.
