# sources/object-store/rustfs/crates/kms/examples/kms_local_demo.rs

## Purpose
`kms_local_demo.rs` is an executable walkthrough for the local KMS backend. It demonstrates global service initialization, local backend configuration, key creation, data-key generation, object encryption/decryption, key listing, cache stats, health check, and shutdown.

## Important APIs, Types, and Functions
The example imports request/response-facing types such as `CreateKeyRequest`, `DescribeKeyRequest`, `GenerateDataKeyRequest`, `ListKeysRequest`, `EncryptionAlgorithm`, `KeySpec`, `KeyUsage`, `KmsConfig`, and `init_global_kms_service_manager`. It uses `KmsConfig::local(...).with_default_key(...).with_cache(true)`, `service_manager.configure`, `start`, `stop`, and `get_global_encryption_service`.

## Control Flow
The demo initializes the global service manager, creates `examples/local_data` if missing, configures a local backend with a default key, starts the service, creates a master key, describes it, optionally generates a data key, encrypts a plaintext object through `encrypt_object`, decrypts it through `decrypt_object`, asserts round-trip equality, lists keys, prints cache stats, checks backend health, and stops the service.

## State and Persistence Behavior
The local backend writes persistent key files under `examples/local_data`. The example creates or reuses that directory but does not remove it. It stores cache state only for the life of the process through the configured service.

## Dependencies and Integration Points
It integrates with the global KMS service manager and high-level object encryption service, not the backend traits directly. It uses `std::io::Cursor` and `tokio::io::AsyncReadExt` to feed/read object data.

## Risks and Edge Cases
The example writes into the repository's `examples/local_data` path, so repeated runs leave keys behind and may collide on fixed key names. Console text includes user guidance and assumes high-level `encrypt_object` will create/use keys as needed. It does not configure a local master key for encryption-at-rest in the shown `KmsConfig::local` call unless defaults do so elsewhere.

## Test Signals
This is an example, not an automated test. It can serve as a manual smoke test for local backend and object encryption round trips.
