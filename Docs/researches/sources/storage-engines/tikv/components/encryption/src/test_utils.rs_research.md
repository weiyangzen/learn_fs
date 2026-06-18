# sources/storage-engines/tikv/components/encryption/src/test_utils.rs

Purpose: Provides small test helpers for creating master-key files and random master keys.

Important APIs and types: `create_master_key_file_test_only` writes a provided hex string plus newline into a temporary `master_key` file and returns its path plus `TempDir`. `generate_random_master_key` returns a hex-encoded random 32-byte key.

Control flow and state: The helper creates temporary filesystem state and relies on the returned `TempDir` to keep it alive. Random generation uses `rand::thread_rng().gen()` and `hex::encode`.

Dependencies and integration: Used by master-key and manager tests that need a `FileBackend`-compatible key file.

Risks: All errors unwrap because this is test-only support. Callers must retain the returned `TempDir`; dropping it removes the key file.

Test signals: No direct tests; heavily used in `file.rs` and `manager/mod.rs` tests.
