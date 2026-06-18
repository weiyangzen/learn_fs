# sources/sync-backup/syncthing/lib/model/folder_recvenc.go

## Purpose
Implements receive-encrypted folder mode by extending send-receive behavior while treating local unexpected plaintext/encrypted items as receive-only changes that can be reverted.

## Important APIs, Types, and Functions
Registers `newReceiveEncryptedFolder` for `config.FolderTypeReceiveEncrypted`. `receiveEncryptedFolder` embeds `*sendReceiveFolder`, sets `localFlags` to `protocol.FlagLocalReceiveOnly`, and implements `Revert`, `revert`, and `revertHandleDirs`.

## Control Flow
`Revert` executes synchronously in the folder service loop. `revert` scans all local files, selects receive-only-changed non-deleted items, queues directories separately, removes non-directories from disk, marks them deleted with zero version while preserving receive-only local flag, flushes batched DB updates, then schedules a pull. Directory handling sorts deepest-first, deletes via send-receive directory deletion helpers, and schedules scans.

## State and Persistence Behavior
Updates local DB entries through `updateLocalsFromScanning`; deletes unexpected files and directories from the folder filesystem. It intentionally keeps `FlagLocalReceiveOnly` on deleted items so they are not advertised as normal valid changes.

## Dependencies and Integration Points
Depends on send-receive deletion helpers, `itererr`, `FileInfoBatch`, `protocol`, and folder service synchronization. Receive-encrypted scanning in `folder.go` uses `scanner.WalkWithoutHashing`, making this revert path part of encrypted-folder local cleanup.

## Risks
Deletion is destructive for unexpected local items. Errors are recorded as scan errors but the routine continues. Directory deletion runs alongside a pull scanner goroutine; scan channel sends must be drained until closed.

## Test Signals
No direct listed tests for receive-encrypted revert. Receive-only tests cover similar revert concepts, but encrypted-specific virtual parent and trailer behavior require separate coverage.
