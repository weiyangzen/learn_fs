# sources/security-integrity/encfs/tests/argon2_integration_test.rs

Purpose: integration coverage for Argon2id-backed EncFS config creation, serialization, loading, cipher derivation, PBKDF2 backward compatibility, and parameter sensitivity.

Important APIs/types/functions: uses `EncfsConfig`, `ConfigType`, `Interface`, `KdfAlgorithm`, `SslCipher::new`, `derive_key_argon2id`, `encrypt_key`, `EncfsConfig::save`, `EncfsConfig::load`, and `EncfsConfig::get_cipher`. Constants `DEFAULT_ARGON2_MEMORY_COST`, `DEFAULT_ARGON2_TIME_COST`, and `DEFAULT_ARGON2_PARALLELISM` define expected defaults.

Control flow: `test_argon2id_config_creation_and_loading` derives a user key blob, encrypts a deterministic volume key, builds a V6 config marked `KdfAlgorithm::Argon2id`, saves to a temp XML file, reloads, asserts Argon2 fields, verifies correct password succeeds, and wrong password fails. `test_pbkdf2_backward_compatibility` loads `encfs6-std.xml` and asserts PBKDF2 fields remain the default for legacy XML. `test_argon2_parameter_sensitivity` derives keys with different memory/time costs and asserts each output differs.

State and persistence: writes a temporary XML config under `std::env::temp_dir()` and removes it. Fixture state is read-only.

Dependencies and integration points: integrates config serialization, KDF selection, OpenSSL cipher setup, and XML fixture parsing.

Risks: deterministic salts and keys are appropriate for tests but not production. The temp filename uses process id, so parallel test processes could collide if run in the same temp directory with identical pids in containers.

Test signals: strong regression signal for Argon2 schema round-trip, wrong-password authentication failure, and preservation of PBKDF2 compatibility.
