# sources/object-store/rustfs/crates/kms/src/api_types.rs

## Purpose
`api_types.rs` defines request/response DTOs for dynamic KMS configuration, service lifecycle/status reporting, and AWS-KMS-like key management operations. It is the contract layer between API handlers/service management and backend configuration/types.

## Important APIs, Types, and Functions
Configuration requests include `ConfigureLocalKmsRequest`, `ConfigureVaultKmsRequest`, `ConfigureVaultTransitKmsRequest`, and tagged enum `ConfigureKmsRequest`. Lifecycle/status types include `ConfigureKmsResponse`, `StartKmsRequest`, `StartKmsResponse`, `StopKmsResponse`, `KmsStatusResponse`, `KmsConfigSummary`, `CacheSummary`, and `BackendSummary`. Key operations include `CreateKeyRequest/Response`, `DeleteKeyRequest/Response`, `ListKeysRequest/Response`, `DescribeKeyRequest/Response`, `CancelKeyDeletionRequest/Response`, `UpdateKeyDescriptionRequest/Response`, `TagKeyRequest/Response`, and `UntagKeyRequest/Response`. Conversion methods turn configuration requests into `KmsConfig`.

## Control Flow
Serde deserializes `ConfigureKmsRequest` by `backend_type`, accepting aliases for local, Vault KV2, and Vault Transit. Vault auth deserialization goes through strict `StrictVaultAuthMethod` to reject unknown fields. `to_kms_config` methods fill defaults for timeout, retries, cache size/TTL, mount names, key paths, TLS skip settings, and `allow_insecure_dev_defaults`. `KmsConfigSummary::from` redacts sensitive values by emitting only booleans and auth method type.

## State and Persistence Behavior
These are pure data types and converters. They do not persist state, but the resulting `KmsConfig` controls backend persistence and cache behavior. Debug for local configure requests redacts `master_key`; Vault auth secret redaction depends on `VaultAuthMethod`'s debug implementation.

## Dependencies and Integration Points
The module depends on `crate::config` for backend config structs, `crate::service_manager::KmsServiceStatus`, and `crate::types::{KeyMetadata, KeyUsage}`. API handlers can deserialize JSON into these types and call `to_kms_config`.

## Risks and Edge Cases
There is a visible contract tension: the earlier imported `ListKeysRequest` from `crate::types` is used in backends, while this file also defines API-facing `ListKeysRequest`/`ListKeysResponse` near the bottom with a different shape. That can confuse imports and documentation. `allow_insecure_dev_defaults` defaults to false, which tests confirm, but callers must surface validation errors clearly. `DescribeKeyResponse` and other bottom DTOs include `success/message` fields in this file's API-facing shape, while backend trait responses in the read source use type aliases/imports from `crate::types`; keeping names distinct is important.

## Test Signals
Unit tests cover backend type aliases, Vault Transit deserialization, local deserialization, rejection of insecure defaults unless opted in, unknown field rejection, start request strictness, Vault Transit summary contents, debug redaction for configure requests, and status summary omission of secrets.
