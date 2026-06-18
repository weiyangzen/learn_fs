# sources/sync-backup/restic/cmd/restic/cmd_unlock.go

Purpose: implements `restic unlock`, removing stale locks or all locks from a repository.

Important APIs/types/functions: `UnlockOptions`; `runUnlock`.

Control flow and state: opens the repository without taking a standard lock via `global.OpenRepository`, selects `repository.RemoveStaleLocks` or `repository.RemoveAllLocks` based on `--remove-all`, runs it, and prints the count when nonzero. Persistent state is deletion of lock files.

Dependencies and integration points: uses repository lock cleanup functions, global repository open, and terminal progress printer.

Risks: `--remove-all` can remove active locks and should be used carefully. Append-only server support is documented in help and depends on repository cleanup implementation.

Test signals: no direct test in this shard; lock behavior is likely covered elsewhere.
