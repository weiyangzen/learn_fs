# sources/sync-backup/kopia/repo/format/upgrade_lock.go

## Purpose
Implements repository format upgrade locking, backup, commit, rollback, and legacy-index poisoning. It coordinates exclusive upgrade access by writing lock intent into the repository format blob.

## Important APIs, Types, And Functions
Constants are `BackupBlobIDPrefix` and `LegacyIndexPoisonBlobID`. Errors include `ErrFormatUptoDate`. Functions/methods are `BackupBlobID`, `Manager.SetUpgradeLockIntent`, `WriteLegacyIndexPoisonBlob`, `Manager.CommitUpgrade`, `Manager.RollbackUpgrade`, and `Manager.GetUpgradeLockIntent`.

## Control Flow
Setting a lock refreshes format, validates intent, and if no lock exists, rejects already-current formats, writes a backup `kopia.repository.backup.<owner>`, stores the lock, and bumps repository config version to `MaxFormatVersion`. Existing locks are updated through `UpgradeLockIntent.Update`. Commit writes a legacy poison index blob, clears the lock, and rewrites config. Rollback lists backup blobs, retains the oldest backup, deletes newer backups, restores the format blob from the oldest backup, deletes that backup, and invalidates cache.

## State And Persistence
Persistent state includes the upgrade lock inside encrypted repository config, backup format blobs, and the legacy poison blob. Rollback primarily restores `kopia.repository`; it does not roll back repository data changes.

## Dependencies And Integration Points
Depends on `blob.Storage`, `gather`, manager refresh/update helpers, and `UpgradeLockIntent`. Repository open/write paths and older clients rely on format version bump and poison blob behavior.

## Risks And Edge Cases
Multiple locks/backups can exist when stale managers set locks from cached state; rollback chooses the oldest backup to restore the original format. Partial failures during backup, restore, or delete are surfaced. Rollback is explicitly dangerous after data format changes because it cannot undo content/index mutations.

## Test Signals
`upgrade_lock_test.go` covers setting/updating locks, already-upgraded rejection, commit/rollback behavior, multiple backup rollback, backup/restore/delete failures, and active writer interruption after lock refresh intervals.
