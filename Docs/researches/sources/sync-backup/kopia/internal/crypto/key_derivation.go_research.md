# sources/sync-backup/kopia/internal/crypto/key_derivation.go

Purpose: derives purpose-specific keys from a primary master key using HKDF-SHA256.

Important APIs/types/functions: `DeriveKeyFromMasterKey` and `errInvalidMasterKey`.

Control flow: rejects nil/empty master keys, then calls `hkdf.Key(sha256.New, masterKey, salt, purpose, length)` and wraps any error.

State and persistence behavior: stateless. Derived keys are returned to callers such as AES-GCM initialization and are not stored by this package.

Dependencies/integration: uses Go `crypto/hkdf` and `crypto/sha256`, plus `pkg/errors`.

Risks/test signals: security depends on non-empty high-entropy master keys and unique purpose strings. Tests assert a stable known vector and error behavior for nil/empty master keys.
