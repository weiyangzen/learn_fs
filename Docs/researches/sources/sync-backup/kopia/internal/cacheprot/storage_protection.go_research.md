# sources/sync-backup/kopia/internal/cacheprot/storage_protection.go

Purpose: defines pluggable protection for local cache entries: no protection, HMAC checksum protection, and authenticated encryption.

Important APIs/types/functions: `StorageProtection`, `NoProtection`, `ChecksumProtection`, `AuthenticatedEncryptionProtection`, `nullStorageProtection`, `checksumProtection`, `authenticatedEncryptionProtection`, and `OverheadBytes`.

Control flow: callers pass cache bytes to `Protect`, which resets the output and writes either raw bytes, HMAC-appended bytes, or AES-GCM-encrypted bytes. `Verify` reverses that process, returning an error on HMAC or decryption failure. Authenticated encryption derives an IV from SHA-256 of the cache item id.

State and persistence behavior: no package-local mutable state. The protected bytes are stored by the cache layer. `OverheadBytes` must match the exact storage overhead because `PersistentCache.Put` reserves space based on it.

Dependencies/integration: uses `gather`, internal `hmac`, `impossible`, and repository `encryption` with algorithm `AES256-GCM-HMAC-SHA256`.

Risks/test signals: deterministic IVs are safe only if each key/id is unique for a stable plaintext write domain. A mismatch between overhead and encryptor output panics in the cache. Tests cover bit-flip detection for HMAC/encryption and pass-through behavior for no protection.
