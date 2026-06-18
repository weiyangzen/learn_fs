# sources/object-store/rustfs/crates/kms/src/types.rs

## Purpose
Defines the core KMS domain model: master/data key metadata, request/response DTOs, object encryption metadata, algorithms, key specs, and operation context.

## Important APIs, Types, And Functions
Key data types include `DataKeyInfo`, `MasterKeyInfo`, `KeyInfo`, `KeyMetadata`, `EncryptionMetadata`, `HealthStatus`, and `ObjectEncryptionContext`. API DTOs include generate/encrypt/decrypt/list/create/describe/generate-data-key/delete/cancel-delete requests and responses. Enums include `KeyUsage`, `KeyStatus`, `EncryptionAlgorithm`, `KeySpec`, and `KeyState`. Helpers include constructors and builder-style context setters, `KeySpec::key_size/as_str`, `EncryptionAlgorithm::as_str/key_size/iv_size`, and `FromStr` for algorithm parsing.

## Control Flow
Most logic is DTO construction and conversion. `DataKeyInfo::clear_plaintext` zeroizes plaintext material and removes it. `Drop for DataKeyInfo` calls that cleanup. `From<MasterKeyInfo> for KeyInfo` maps metadata into both metadata and tags.

## State And Persistence
All major structs derive serde traits and form persisted/wire schemas for KMS APIs and object metadata. `DataKeyInfo` has explicit memory hygiene for optional plaintext bytes, while many request/response structs containing plaintext vectors rely on caller lifecycle and do not zeroize on drop.

## Dependencies And Integration
Used throughout manager, backends, service, and API layers. Depends on `jiff::Zoned`, serde, `HashMap`, `uuid`, and `zeroize`.

## Risks And Edge Cases
There is overlap between older generic types (`GenerateKeyRequest`, `MasterKeyInfo`, `DataKeyInfo`) and newer KMS-like DTOs (`GenerateDataKeyRequest`, `KeyMetadata`), which may cause integration confusion. `EncryptionMetadata.encrypted_at` uses plain `Zoned` serde rather than `time_serde`, so compatibility differs from `DataKeyEnvelope`. `From<MasterKeyInfo>` clones metadata and also uses it as tags, conflating two concepts.

## Test Signals
No direct tests in this file; behavior is exercised through backend, manager, and service tests that construct these DTOs and validate serde/algorithm behavior indirectly.
