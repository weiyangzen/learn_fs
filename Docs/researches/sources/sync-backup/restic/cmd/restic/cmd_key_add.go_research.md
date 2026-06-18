# sources/sync-backup/restic/cmd/restic/cmd_key_add.go

Purpose: implements `restic key add`, adding another password/key record to a repository.

Important APIs/types/functions: `KeyAddOptions`; `runKeyAdd`; `addKey`; `getNewPassword`; `switchToNewKeyAndRemoveIfBroken`; test-only `testKeyNewPassword`.

Control flow and state: `runKeyAdd` rejects arguments, opens the repository with an append lock, gets a new password from a test override, `--new-insecure-no-password`, `--new-password-file`, or interactive double prompt, then calls `repository.AddKey` with current key material. It immediately searches the new key; if validation fails it removes the broken key. Persistent state is a new key file, with rollback attempt on failure.

Dependencies and integration points: uses global password loading/prompting and repository key APIs. Append lock permits adding key data without exclusive snapshot mutation.

Risks: empty-password behavior is intentionally gated. The test override is global package state and must be reset. Rollback ignores remove errors, so a broken key may remain if backend removal fails.

Test signals: key integration tests cover adding normal keys, username/hostname metadata, invalid option combinations, empty password policy, empty-password opt-in, and backend-corruption failure recovery.
