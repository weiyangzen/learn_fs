# sources/storage-engines/tikv/components/encryption/src/config.rs

Purpose: This module defines user-facing and protobuf-facing encryption configuration types, including data encryption method selection, data-key rotation, file/KMS master-key configuration, and vendor-specific KMS subconfig conversion.

Important APIs and types: Key types are `EncryptionConfig`, `FileConfig`, `AzureConfig`, `GcpConfig`, `AwsConfig`, `KmsConfig`, and `MasterKeyConfig`. Important methods are `KmsConfig::from_proto`, `KmsConfig::to_cloud_config`, `MasterKeyConfig::from_proto`, and custom serde helpers for `EncryptionMethod`.

Control flow: Defaults choose plaintext data encryption, seven-day rotation, enabled file dictionary log, threshold one million, and plaintext current/previous master keys. KMS config conversion copies common key/location/vendor fields and optional Azure/GCP/AWS nested fields, translating empty proto strings to `None`. `to_cloud_config` validates non-empty key IDs through `cloud::kms::KeyId::new`.

State and persistence behavior: These structs are serialized/deserialized from TOML and protobuf, and `OnlineConfig` marks most encryption settings as skipped for online changes. Secret-bearing Azure fields are intentionally omitted from `Debug`.

Dependencies and integration points: It depends on `cloud::kms` subconfigs, `kvproto::encryptionpb`, serde, `online_config`, `ReadableDuration`, and crate `Error`.

Risks: Configuration shape is security-sensitive. Empty strings become `None` only in proto conversion, while TOML parsing follows serde defaults. Most fields are not online-configurable. `MasterKeyConfig::from_proto` returns `None` if the oneof is absent, leaving callers to decide defaults.

Test signals: Unit tests cover TOML parsing for AWS/Azure/GCP KMS, proto-to-config conversion with vendor-specific fields, cloud-config conversion, and empty key-id rejection.
