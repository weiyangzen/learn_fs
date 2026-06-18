# sources/storage-engines/pebble/internal/deletepacer/obsolete_file.go

## Purpose
`obsolete_file.go` defines the delete pacer’s file descriptor type and the rule for whether a file contributes bytes to pacing.

## Important APIs, Types, And Functions
`ObsoleteFile` records `FileType`, `FS`, `Path`, `FileNum`, approximate `FileSize`, and `Placement`. Its unexported `pacingBytes` method returns `FileSize` only for local table and blob files; all other file types or non-local placements return zero.

## Control Flow
There is no asynchronous control flow in this file. Callers construct `ObsoleteFile` values and the pacer consults `pacingBytes` before adding recent history, queued bytes, and debt.

## State And Persistence Behavior
The struct describes existing filesystem objects but does not persist anything itself. `FileSize` is advisory for logs and exact enough for table/blob pacing. The actual deletion is delegated to the pacer’s delete callback and `vfs.FS`.

## Dependencies And Integration Points
It integrates with Pebble `base.FileType`, `base.DiskFileNum`, `base.Placement`, and `vfs.FS`. It is consumed by `DeletePacer.Enqueue` and the rate/debt logic in the deletepacer package.

## Risks And Edge Cases
Remote or shared-object placements are deliberately unpaced because deleting them does not reclaim local disk in the same way. If new reclaim-heavy local file types are added but not included here, the pacer will undercount deletion work. Approximate sizes can skew pacing but not correctness.

## Test Signals
The datadriven deletepacer tests use local table files, exercising the positive path. Additional targeted tests would check non-local, blob, log, and unknown file type behavior.
