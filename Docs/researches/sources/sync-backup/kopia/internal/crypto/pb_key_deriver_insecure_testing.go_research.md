# sources/sync-backup/kopia/internal/crypto/pb_key_deriver_insecure_testing.go

Purpose: testing-only password key deriver that produces fast deterministic keys for tests.

Important APIs/types/functions: build tag `testing`, `TestingOnlyInsecurePBKeyDerivationAlgorithm`, `insecureKeyDeriver`, and its `deriveKeyFromPassword`.

Control flow: init registers the algorithm name. Derivation hashes only the password with SHA-256 and returns the requested prefix of the digest.

State and persistence behavior: mutates the package-global key-deriver registry at init. No persistent state.

Dependencies/integration: used by tests that need password derivation without PBKDF2/scrypt cost.

Risks/test signals: intentionally ignores salt and is insecure; build tag must prevent production inclusion. If `keySize` exceeds SHA-256 length it will panic by slicing beyond the digest, so tests should request safe sizes.
