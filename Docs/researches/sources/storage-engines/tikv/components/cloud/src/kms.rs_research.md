# sources/storage-engines/tikv/components/cloud/src/kms.rs

## Purpose
Defines shared KMS configuration, key wrapper types, cryptography key metadata, and the `KmsProvider` trait implemented by cloud provider crates.

## Important APIs, Types, And Functions
- `Location` stores region and endpoint.
- `SubConfigAzure`, `SubConfigGcp`, and `SubConfigAws` hold provider-specific credential/config settings.
- `Config` stores `KeyId`, vendor, location, and optional provider subconfigs.
- `Config::from_proto`, `from_azure_kms_config`, and `from_gcp_kms_config` convert `MasterKeyKms` protobuf data.
- `KeyId::new` rejects empty IDs.
- `EncryptedKey::new` rejects empty ciphertext and exposes `into_inner`/`as_raw`.
- `CryptographyType`, `PlainKey`, `DataKeyPair`, and `KmsProvider` define key material contracts and provider operations.

## Control Flow
Provider-specific code receives or constructs `Config`, validates `KeyId`, creates provider clients, and returns `DataKeyPair`s with `PlainKey::new` and `EncryptedKey::new`. Shared constructors centralize empty-key and AES-256 length validation.

## State And Persistence Behavior
The file stores no runtime state. Wrapper types preserve invariants for in-memory key material and prevent accidental plaintext key exposure in debug logs.

## Dependencies And Integration Points
Depends on `kvproto::encryptionpb::MasterKeyKms`, `derive_more::Deref`, `async_trait`, and shared cloud errors. Azure/GCP/AWS KMS implementations all target `KmsProvider`.

## Risks And Edge Cases
`Config` can contain mismatched `vendor` and subconfig fields; provider constructors must validate their expected subconfig. `PlainKey` derefs to `Vec<u8>`, so callers can still clone/expose plaintext. Adding algorithms requires updating `target_key_size`. Empty `Location.endpoint` conventionally means default endpoint.

## Test Signals
No direct tests. Invariants are exercised indirectly by provider tests that construct `KeyId`, `EncryptedKey`, and `PlainKey`.
