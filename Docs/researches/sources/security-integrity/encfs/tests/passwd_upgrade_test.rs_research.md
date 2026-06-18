# sources/security-integrity/encfs/tests/passwd_upgrade_test.rs

Purpose: verifies password/KDF upgrade from PBKDF2-backed config data to Argon2id-backed config data while preserving the decrypted volume key.

Important APIs/types/functions: uses `EncfsConfig`, `ConfigType`, `Interface`, `KdfAlgorithm`, Argon2 constants, `SslCipher`, and `getrandom::fill`. The test derives a PBKDF2 user key, encrypts a deterministic volume key, builds a V6 config, decrypts it with the old password, re-encrypts the same volume key under Argon2id parameters and a new password, saves/reloads, and validates the new cipher.

Control flow: constructs cipher/name interfaces, salt, volume key/IV blob, and PBKDF2-encrypted key data for `test_password_123`. After verifying the original config works, it derives the old wrapping key, decrypts the volume blob, generates a fresh 20-byte salt, switches KDF metadata to Argon2id defaults, derives a new wrapping key for `new_password_456`, re-encrypts the volume blob, asserts the old password fails and the new password succeeds, then persists and reloads the config to assert `KdfAlgorithm::Argon2id`.

State and persistence: writes an upgraded temp config and cleans it up.

Dependencies and integration points: integrates KDF derivation, key wrapping, config schema fields, save/load, and `get_cipher`.

Risks: test uses deterministic volume material and simulated upgrade logic rather than invoking a dedicated CLI command, so it validates primitives more than command wiring. The temp filename is pid-based and could collide in unusual parallel runs.

Test signals: protects key-material continuity across KDF migration and checks Argon2 field persistence.
