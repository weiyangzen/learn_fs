<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_unlock.go -->
# sources/sync-backup/git-lfs/commands/command_unlock.go

Purpose: implements `git lfs unlock`, releasing locks by path or lock ID, with force and JSON modes.

Important APIs/types/functions: `unlockFlags`, `unlockResponse`, `handleUnlockError`, `unlockCommand`, `unlockAbortIfFileModified`, and `unlockAbortIfFileModifiedById`; `locking.Client.UnlockFile`, `UnlockFileById`, and `SearchLocks`.

Control flow: requires exactly one of path args or `--id`, applies optional remote override, creates lock client with remote ref, then for paths normalizes each path, rejects modified files unless `--force`, unlocks, and records JSON/text results. For ID mode it first tries to resolve lock path from local cache then server to check modification state, unlocks by ID, and reports result. Partial failures exit code 2.

State and persistence behavior: releases remote locks and updates local lock cache through client internals. It reads working-tree modification state and may allow nonexistent forced paths.

Dependencies/integration points: shares lock path normalization and JSON flag with lock/locks, depends on Git file modification checks and lock API behavior.

Risks and test signals: risks include ID mode ignoring returned error from `unlockAbortIfFileModifiedById`, path fallback with force using unnormalized user input, partial success semantics, and stale local cache path resolution. Test signals include path unlock, ID unlock, modified file rejection, force modified/nonexistent unlock, JSON success/failure arrays, remote override, and server errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_unlock.go -->
