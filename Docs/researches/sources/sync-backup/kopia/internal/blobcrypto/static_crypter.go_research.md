## sources/sync-backup/kopia/internal/blobcrypto/static_crypter.go

Purpose: simple `Crypter` implementation holding fixed hashing and encryption functions.

Important APIs/types/functions: `StaticCrypter`, `Encryptor`, and `HashFunc`.

Control flow, state, and persistence: methods return the struct fields without mutation. The type has no lifecycle or persistence.

Dependencies and integration points: useful in tests and format-derived crypto setup, because it adapts `hashing.HashFunc` and `encryption.Encryptor` to the `Crypter` interface.

Risks and test signals: nil fields are not guarded; callers must construct it correctly. Blob crypto tests exercise it with valid and deliberately bad components.
