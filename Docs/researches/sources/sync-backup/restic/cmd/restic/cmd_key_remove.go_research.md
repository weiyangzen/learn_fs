# sources/sync-backup/restic/cmd/restic/cmd_key_remove.go

Purpose: implements `restic key remove [ID]`, deleting a non-current key from the repository.

Important APIs/types/functions: `runKeyRemove`; `deleteKey`.

Control flow and state: the command requires exactly one key ID/prefix, opens with an exclusive lock, resolves the key through `restic.Find`, rejects removal of the active key, removes the key file through `repository.RemoveKey`, and prints confirmation.

Dependencies and integration points: uses repository key storage, restic file prefix matching for `KeyFile`, progress terminal output, and exclusive locking.

Risks: ambiguous or invalid ID prefix behavior is delegated to `restic.Find`. Refusing current-key removal is critical to prevent self-lockout.

Test signals: key integration tests remove all non-current keys, verify repository accessibility with the last password, and cover missing/extra argument errors.
