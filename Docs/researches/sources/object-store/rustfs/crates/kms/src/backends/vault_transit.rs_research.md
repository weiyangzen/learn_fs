# sources/object-store/rustfs/crates/kms/src/backends/vault_transit.rs

## Purpose
`vault_transit.rs` implements a KMS backend backed by HashiCorp Vault Transit. Unlike the KV2 backend, cryptographic encrypt/decrypt operations are delegated to Vault Transit keys, while RustFS-specific metadata is tracked in an in-memory cache.

## Important APIs, Types, and Functions
`TransitKeyMetadata` stores usage, description, tags, state, creation/deletion dates, origin, creator, and current version. `VaultTransitKmsClient` holds a `VaultClient`, `VaultTransitConfig`, and `RwLock<HashMap<String, TransitKeyMetadata>>`. Helpers include `canonicalize_context`, `map_vault_error`, `read_transit_key`, `create_transit_key`, `transit_encrypt`, `transit_decrypt`, metadata cache accessors, `key_info`, `key_metadata_response`, and `ensure_key_active`. `VaultTransitKmsBackend` wraps the client and implements the simplified API trait.

## Control Flow
Client construction configures Vault address, token auth, and optional namespace; AppRole is rejected as unimplemented. Key creation creates an AES-256-GCM96 Transit key and stores metadata in memory. Data-key generation creates plaintext DEK material locally, encrypts it with Vault Transit using canonicalized encryption context as associated data, stores Transit ciphertext bytes in a `DataKeyEnvelope`, and returns serialized envelope. Decryption parses the envelope, validates context compatibility, decodes the Transit ciphertext, and asks Vault to decrypt. Direct encrypt/decrypt uses Transit ciphertext bytes for `EncryptResponse`; the simplified backend decrypt path expects a `DataKeyEnvelope`.

## State and Persistence Behavior
Vault Transit persists cryptographic keys. RustFS metadata such as descriptions, tags, deletion state, origin, and creation date is only held in `metadata_cache`. If metadata is missing after restart, `get_key_metadata` reads the Transit key and synthesizes default metadata. Deletion with pending windows is represented in this in-memory metadata until force deletion removes the Transit key.

## Dependencies and Integration Points
The file uses `vaultrs::transit::{data, key}` and Transit request builders, base64, `jiff::Zoned`, KMS config/types/errors, and Tokio `RwLock`. It supports constructing from either explicit Vault Transit config or a Vault KV2 config by extracting address/auth/namespace/mount path.

## Risks and Edge Cases
Metadata is not persisted, so key states, tags, descriptions, and scheduled deletion dates are lost across process restarts and can be synthesized as enabled. `health_check` fails if listing Transit keys is not permitted, even if encrypt/decrypt permissions exist. `KmsClient::decrypt` expects a data-key envelope and cannot directly decrypt bytes returned by `KmsClient::encrypt`; this mirrors a broader direct-encrypt contract mismatch. Pending deletion is only enforced by `ensure_key_active`, so synthesized metadata after restart may allow use of previously pending keys. AppRole remains unimplemented.

## Test Signals
No tests are defined in this file. Behavior must be validated through higher-level service tests or live Vault integration tests elsewhere.
