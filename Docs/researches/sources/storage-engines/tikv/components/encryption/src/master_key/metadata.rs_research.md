# sources/storage-engines/tikv/components/encryption/src/master_key/metadata.rs

Purpose: Centralizes string keys and byte markers used in `EncryptedContent.metadata` for master-key encryption formats.

Important APIs and types: `MetadataKey` variants are `Method`, `Iv`, `AesGcmTag`, `KmsVendor`, and `KmsCiphertextKey`; `as_str` maps them to stable metadata names. `MetadataMethod` variants are `Plaintext` and `Aes256Gcm`; `as_slice` maps them to stable byte values.

Control flow and state: This is a pure constant/enum mapping module with no mutable state. Other backends use it to write and validate metadata.

Dependencies and integration: Imported by plaintext, memory, file, and KMS backends. The string names are part of the persisted encrypted metadata contract, so changing them would break dictionary/key compatibility.

Risks: There is no version negotiation here; unsupported methods are handled by callers. Typos or changes in constants would make existing metadata unreadable.

Test signals: No local tests, but all master-key backend tests exercise these metadata names through successful and failing decrypt paths.
