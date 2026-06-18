
# sources/sync-backup/restic/internal/repository/key.go

Purpose: manages repository key files: encrypted master keys stored as raw backend key files and unlocked from a user password. The central type is `Key`, containing metadata, scrypt KDF parameters, salt, encrypted master-key data, derived user key, master key, and backend ID.

Important APIs are `AddKey`, `LoadKey`, `RemoveKey`, `searchKey`, `openKey`, and `createMasterKey`. `AddKey` calibrates or reuses global scrypt parameters, fills host/user metadata, derives a user key, encrypts either a new or template master key, hashes the resulting JSON, and saves it as `KeyFile`. `searchKey` optionally resolves a prefix hint via `restic.Find`, then lists key files until one decrypts or limits are reached.

State and persistence are explicit: key JSON is saved directly through `repo.be.Save`, not through encrypted unpacked storage, because key files bootstrap encryption. Risks include global mutable KDF params, hint lookup ambiguity, password-authentication errors being used for iteration, and refusal to remove the active key. Integration points include repository initialization/opening, config loading, crypto KDF/seal/open, backend handles, and restic ID prefix search. Test signals are mostly indirect through repository test helpers that lower KDF parameters and open initialized repositories.
