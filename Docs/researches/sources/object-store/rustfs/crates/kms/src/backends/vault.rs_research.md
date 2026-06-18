# sources/object-store/rustfs/crates/kms/src/backends/vault.rs

## Purpose
`vault.rs` implements a Vault KV2-backed KMS backend using `vaultrs`. Despite comments about Transit, this file stores key data and base64-encoded key material in Vault KV2 and performs data-key wrapping locally with `AesDekCrypto`.

## Important APIs, Types, and Functions
`VaultKmsClient` holds a `VaultClient`, `VaultConfig`, KV mount, key path prefix, and `AesDekCrypto`. `VaultKeyData` is the serialized Vault record with algorithm, usage, timestamps/status/version, description, metadata/tags, and `encrypted_key_material`. Helpers include `new`, `key_path`, `encrypt_key_material`, `decrypt_key_material`, `get_key_material`, `encrypt_with_master_key`, `decrypt_with_master_key`, `store_key_data`, `store_key_metadata`, `get_key_data`, `list_vault_keys`, and physical `delete_key`. `VaultKmsBackend` wraps the client and updates API-facing metadata.

## Control Flow
Client construction builds Vault settings with token auth and optional namespace; AppRole returns an unimplemented backend error. Key creation checks KV existence, generates AES key material, base64 encodes it, and stores a `VaultKeyData` record. Data-key generation creates plaintext DEK material, encrypts it with master key material through local AEAD, stores encrypted DEK/nonce/context in `DataKeyEnvelope`, and returns the serialized envelope. Decrypt parses that envelope, validates encryption context compatibility, and unwraps the DEK. Listing uses `kv2::list` and describes each key. Delete either marks keys pending deletion or physically deletes KV metadata on force-immediate when already pending.

## State and Persistence Behavior
Key metadata and key material persist in Vault KV2 under `{key_path_prefix}/{key_id}` in `kv_mount`. Key material is only base64 encoded by `encrypt_key_material`; comments explicitly say production should use Transit for additional encryption, but the current implementation does not. Runtime state is mostly in Vault; there is no local metadata cache in this file.

## Dependencies and Integration Points
The backend depends on `vaultrs::kv2`, Vault client settings, KMS config/types/errors, local encryption helpers, base64, serde, jiff, and tracing. It implements both backend traits and is used by `KmsConfig::vault`/Vault KV2 configuration.

## Risks and Edge Cases
Key material in Vault KV2 is not cryptographically wrapped by Vault Transit in this implementation, just base64 encoded. `get_key_material` self-heals missing, undecodable, or wrong-length key material by generating new material and storing it, which can permanently break decryption of data encrypted with the old material. `encrypt` uses a simple XOR of plaintext with key material rather than AEAD, while data-key wrapping uses `AesDekCrypto`; direct encrypt/decrypt semantics are inconsistent. `cancel_key_deletion` builds an enabled response but does not call `update_key_metadata_in_storage`, so the pending state may remain persisted. AppRole is accepted in config types but rejected at client construction.

## Test Signals
The only test is ignored and requires a running Vault instance. It covers client creation, key creation/description, data-key generation, and health check. There are no active unit tests for deletion, cancellation, metadata persistence, or the self-healing key-material paths.
