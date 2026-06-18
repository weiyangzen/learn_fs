# sources/storage-engines/tikv/components/encryption/src/backup/backup_encryption.rs

Purpose: `BackupEncryptionManager` groups encryption dependencies and helper operations used by backup/log-backup flows.

Important APIs and types: The struct stores an optional user-supplied plaintext `CipherInfo`, a `master_key_based_file_encryption_method`, a `MultiMasterKeyBackend`, and an optional TiKV `DataKeyManager`. Public methods are `new`, inherent `default`, `opt_data_key_manager`, async `encrypt_data_key`, async `decrypt_data_key`, async `is_master_key_backend_initialized`, and `generate_data_key`.

Control flow: Data-key encryption/decryption delegates to the multi-master-key backend. Initialization readiness requires a non-`Unknown`, non-`Plaintext` method and an initialized backend. Data-key generation delegates to the backend using the configured encryption method.

State and persistence behavior: The manager is cloneable and holds backend/key-manager handles, but does not itself persist data. The optional plaintext data key is specifically documented as intended for stream backup uploads and not recommended in production.

Dependencies and integration points: It integrates backup protobuf `CipherInfo`, encryption protobuf `EncryptedContent`/`EncryptionMethod`, `DataKeyManager`, and `MultiMasterKeyBackend`.

Risks: The inherent `default` is not a `Default` trait implementation, which may surprise generic callers. Readiness depends on async backend state and encryption method consistency. Plaintext data-key support is operationally sensitive.

Test signals: No direct tests in this file; coverage likely comes from backup workflows that exercise key encryption and readiness checks.
