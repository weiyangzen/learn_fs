<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/lockverifier.go -->
# sources/sync-backup/git-lfs/commands/lockverifier.go

Purpose: lock verification support for uploads/pre-push, detecting LFS files locked by other users across refs and honoring per-endpoint locksverify configuration.

Important APIs/types/functions: `verifyState` enum, `verifyLocksForUpdates`, `lockVerifier`, methods `Verify`, `addLocks`, `Contains`, `LockedByThem`, `LockedByUs`, `UnownedLocks`, `HasUnownedLocks`, `OwnedLocks`, `HasOwnedLocks`, `Enabled`, `newRefLocks`; constructor `newLockVerifier`; `refLock` with `Path`, `Owners`, `Add`; and `getVerifyStateFor`.

Control flow: for each remote ref update, `Verify` skips disabled/already-verified refs, queries `SearchLocksVerifiable`, disables verification on not-implemented, warns or exits for auth/API errors depending on configured state, suggests enabling/disabling config for unknown support, records our/their locks by path, and marks the ref verified. Scanner-set methods classify changed names as locked by us/them and collect matched locks for later reporting.

State and persistence behavior: in-memory maps of verified refs, our locks, their locks, owned/unowned matches, and endpoint verify state. `disableFor`/`supportsLockingAPI` are external and may update config/cache outside this file.

Dependencies/integration points: integrates transfer manifest standalone detection, lock API client, endpoint URL config via `config.NewURLConfig`, upload scanning, and Git ref update structures.

Risks and test signals: risks include panicking on nil ref, owner nil assumptions in `Owners`, duplicate owned/unowned entries on repeated classification, support auto-detection changing default enabled state, and auth errors being warning-only in unknown mode. Test signals include standalone transfer disabled, explicit true/false locksverify, unknown supported/unsupported endpoints, auth failure, not implemented disabling, multiple refs same path owners string, and scanner `Contains`/LockedByThem/LockedByUs behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/lockverifier.go -->
