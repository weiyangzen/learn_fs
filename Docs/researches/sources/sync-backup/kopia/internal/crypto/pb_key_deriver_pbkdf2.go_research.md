# sources/sync-backup/kopia/internal/crypto/pb_key_deriver_pbkdf2.go

Purpose: registers and implements PBKDF2-SHA256 password-based key derivation.

Important APIs/types/functions: `Pbkdf2Algorithm`, constants for minimum salt length and iterations, `pbkdf2KeyDeriver`, init registration, and `deriveKeyFromPassword`.

Control flow: init registers algorithm `pbkdf2-sha256-600000` with 600,000 iterations and 16-byte minimum salt. Derivation rejects short salts, calls `pbkdf2.Key(sha256.New, password, salt, iterations, keySize)`, wraps errors, and returns the derived key.

State and persistence behavior: updates the global deriver registry during init. Derived keys are returned only to callers.

Dependencies/integration: used by `DeriveKeyFromPassword`; imports Go `crypto/pbkdf2`, `sha256`, and `pkg/errors`.

Risks/test signals: high iteration count impacts latency by design. Error string has typo "atleast". No direct listed test covers PBKDF2 vectors or short salt behavior in this work item.
