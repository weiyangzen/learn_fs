# sources/sync-backup/syncthing/lib/model/folder_recvonly.go

## Purpose
Implements receive-only folder mode, where local changes are tracked but not propagated, and user-triggered revert resets or deletes local changes to return to global state.

## Important APIs, Types, and Functions
Registers `newReceiveOnlyFolder` for `config.FolderTypeReceiveOnly`. `receiveOnlyFolder` embeds `*sendReceiveFolder`, sets `localFlags` to `protocol.FlagLocalReceiveOnly`, and implements `Revert`/`revert`. `deleteQueue` batches deletions, especially directories, with `handle` and `flush`.

## Control Flow
`revert` runs in the folder loop, starts a pull scanner routine, iterates all local files, and ignores entries without receive-only local changes. It clears the receive-only flag, compares with the global file, deletes unexpected local-only items, merges equivalent global entries, or resets versions to zero so the next pull wins without conflict. Directory deletes are queued and processed deepest-first after file updates, then deleted directories are appended as deleted DB entries.

## State and Persistence Behavior
Mutates local database through `updateLocalsFromScanning`, removes files/directories from disk when local-only, clears local flags, and schedules a pull so missing global content is downloaded. No remote index should be advanced by receive-only changes because local flags are converted when advertised.

## Dependencies and Integration Points
Depends on `sendReceiveFolder` pull/delete helpers, `itererr`, `FileInfoBatch`, `events`, `ignore.Matcher`, and `protocol.FileInfo` comparison rules. Model API calls `Revert` for receive-only folders.

## Risks
Revert is intentionally destructive for unexpected local items. Ignored but non-deletable items are skipped. Some `FlushIfFull` calls ignore returned errors inside the loop, which may delay error reporting until final flush. Correctness depends on subtle `FileInfoComparison` flags for ownership and xattrs.

## Test Signals
`folder_recvonly_test.go` extensively covers deletion of unexpected files, reset-to-need behavior, undoing local changes, remote drop handling, remote adoption of identical changes, own-ID version regression, and avoiding conflict loops.
