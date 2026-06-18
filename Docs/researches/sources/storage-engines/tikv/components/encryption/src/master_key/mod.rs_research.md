# sources/storage-engines/tikv/components/encryption/src/master_key/mod.rs

Purpose: Defines the master-key abstraction layer and combines plaintext, file, KMS, and multi-master-key restore behavior.

Important APIs and types: `Backend` is the sync encrypt/decrypt/security trait. `AsyncBackend` is the async variant. `PlaintextBackend` stores content without encryption but validates plaintext metadata. `MultiMasterKeyBackend` asynchronously maintains an optional ordered backend list and configs, with update, encrypt, decrypt, `generate_data_key`, and `is_initialized` APIs.

Control flow: Plaintext encryption writes `method=plaintext`; decrypt refuses non-plaintext metadata as `WrongMasterKey`. `MultiMasterKeyBackend::update_from_proto_if_needed` converts protobuf master keys to configs, and `update_from_config_if_needed` rebuilds backend objects only when configs change. Encryption/decryption clones the current backend vector under a read lock, tries backends in order, returns the first success, and combines error messages if all fail.

State and persistence behavior: Plaintext backend has no state. Multi-master-key state is an async `RwLock` containing optional configs and backend vector; configs and backends are updated together. It does not persist state itself, but decrypts persisted `EncryptedContent` produced by one of the configured backends.

Dependencies and integration: Used by backup/restore and by `DataKeyManager` master-key operations. Depends on `MasterKeyConfig`, protobuf `MasterKey`, generated data-key helper, and concrete file/KMS modules.

Risks: Multi-backend errors are string-combined into `Other`, so structured error codes are lost after all attempts fail. Backend creation is synchronous inside the write lock. Plaintext backend is deliberately insecure; manager rejects enabling encryption with insecure current master key.

Test signals: Tests provide `MockBackend` for manager fallback tests and async mock backends for multi-master-key failure aggregation and first-success behavior with multiple backends.
