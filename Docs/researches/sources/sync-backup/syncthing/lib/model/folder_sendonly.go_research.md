# sources/sync-backup/syncthing/lib/model/folder_sendonly.go

## Purpose
Implements send-only folder behavior: never downloads file content, but can merge metadata-only differences and allow the local side to override global state.

## Important APIs, Types, and Functions
Registers `newSendOnlyFolder` for `config.FolderTypeSendOnly`. `sendOnlyFolder` embeds `*folder`, implements `PullErrors`, `pull`, `Override`, and `override`.

## Control Flow
`pull` iterates needed global files alphabetically. Ignored files are invalidated locally, missing invalid/deleted entries can be accepted for accounting, and files equivalent to current local state except allowed metadata differences are merged into the local DB. `override` iterates needed globals, skips invalid local states, marks missing local files as deleted, or merges local versions with needed versions and updates the local version with the local short ID.

## State and Persistence Behavior
Writes local DB batches through `updateLocalsFromPulling` and `updateLocalsFromScanning`. It does not perform content IO during pull, and `PullErrors` always returns nil. Override changes local version vectors and sequence reset to force database sequencing.

## Dependencies and Integration Points
Depends on `itererr`, `FileInfoBatch`, `config`, `ignore`, `protocol`, and folder base scheduling. The base `folder.pull` treats send-only specially by not taking the IO limiter for content transfer.

## Risks
Send-only semantics are subtle: accepting metadata-only global entries must not hide real content differences. Override can propagate local deletions for missing files, so UI/API access should remain deliberate. `batch.Flush()` return in `pull` is not checked.

## Test Signals
No direct listed send-only tests in this subset. Behavior is likely covered elsewhere in model tests; this file would benefit from focused tests for metadata merge, ignored need invalidation, and override version vector updates.
