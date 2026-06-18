## sources/sync-backup/restic/internal/repository/crypto/kdf.go

Purpose: scrypt-based key derivation and salt generation for repository passwords.

Important APIs/types: `Params` stores scrypt `N`, `R`, and `P`. `DefaultKDFParams` mirrors `simple-scrypt` defaults. `Calibrate(timeout, memory)` asks `simple-scrypt` to choose parameters under runtime constraints. `KDF(p, salt, password)` validates 64-byte salt and parameter sanity, derives 64 bytes with scrypt, copies the first 32 bytes to `EncryptionKey`, and the next 32 bytes to `MACKey` as `k||r`. `NewSalt` returns 64 random bytes and panics if entropy fails.

Control flow and state: KDF is deterministic for the same password/salt/params. It performs parameter validation before expensive derivation. Salt generation is random and no persistent state is stored here.

Dependencies and integration points: used by repository key creation/search. Integrates `github.com/elithrar/simple-scrypt`, `golang.org/x/crypto/scrypt`, and crypto key layout from `crypto.go`.

Risks and test signals: security depends on calibrated parameters, adequate memory/time settings, and storing salts accurately. Salt length is strict; mismatches fail. `TestCalibrate` smoke-tests calibration but does not assert exact parameters because hardware varies.
