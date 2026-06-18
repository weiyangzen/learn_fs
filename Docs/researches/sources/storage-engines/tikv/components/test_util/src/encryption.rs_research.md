# Research: sources/storage-engines/tikv/components/test_util/src/encryption.rs

## sources/storage-engines/tikv/components/test_util/src/encryption.rs

Purpose: builds file-based encryption fixtures for tests. It creates deterministic master key files and `EncryptionConfig`/`DataKeyManager` instances backed by `encryption_export`.

Important APIs are `create_test_key_file`, `new_test_file_master_key`, `new_file_security_config`, and `new_test_key_manager`. The key file contains a fixed hex key. `new_file_security_config` selects AES-256-CTR, seven-day data key rotation, dictionary logging, a high rewrite threshold, and the same file master key as current and previous. `new_test_key_manager` creates current and previous backends and configures low dictionary rewrite threshold for tests.

Control flow writes files into a temp path, constructs master key configs, then calls `DataKeyManager::new` with backend factories and rotation/dictionary arguments. State and persistence are the test key file and data key dictionary under the temp directory.

Dependencies include `encryption_export`, `kvproto::encryptionpb::EncryptionMethod`, `ReadableDuration`, `tempfile`, and standard file IO. Risks include fixed key material, unwraps on file writes and path conversion, and test behavior differing from production key management. Test signals are successful key-manager creation and downstream encrypted Rocks/storage tests reading dictionary files.
