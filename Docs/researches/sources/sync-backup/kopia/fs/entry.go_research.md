<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/entry.go -->
# sources/sync-backup/kopia/fs/entry.go

## Purpose
Defines core virtual filesystem interfaces and utility functions used throughout snapshot, restore, localfs, virtualfs, and snapshotfs code.

## Important APIs, Types, And Functions
Key definitions are `Entry`, `OwnerInfo`, `DeviceInfo`, `Reader`, `File`, `StreamingFile`, `Directory`, `DirectoryIterator`, `DirectoryWithSummary`, `ErrorEntry`, `EntryWithError`, `DirectorySummary`, `Symlink`, `ErrUnknown`, `ErrEntryNotFound`, and `ModBits`. Helpers include `IterateEntries`, `GetAllEntries`, `IterateEntriesAndFindChild`, `DirectorySummary.Clone`, `FindByName`, and `Sort`.

## Control Flow
Directory utilities use the iterator contract: call `Iterate`, defer `Close`, call `Next` until nil entry, propagate iterator or callback errors, and wrap callback failures with entry names.

## State And Persistence Behavior
The file has no persistent state. It defines data shapes that are persisted elsewhere, especially `DirectorySummary` JSON fields in snapshot metadata.

## Dependencies And Integration Points
Integrates Go `os.FileInfo`, `io` interfaces, sort/search utilities, and package timestamp type `UTCTimestamp`.

## Risks And Edge Cases
`FindByName` assumes sorted input; callers using unsorted slices get undefined lookup results. `DirectorySummary.Clone` shallow-copies entry objects but copies the slice. Iterator contract says calling Next after end is undefined.

## Test Signals
Tests cover sort and binary search. Broader integration tests across snapshot upload/restore validate interface contracts.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/entry.go -->
