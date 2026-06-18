# sources/storage-engines/tikv/components/cloud/azure/src/kms.rs

## Purpose
Implements Azure Key Vault/Managed HSM as a `cloud::kms::KmsProvider`. It generates plaintext data keys with Azure Managed HSM random bytes, encrypts them with a Key Vault key, and decrypts encrypted data keys for TiKV encryption-at-rest workflows.

## Important APIs, Types, And Functions
- `AzureKms` stores tenant/client identifiers, Key Vault and HSM `KeyClient`s, the current `KeyId`, and service URLs/names for redacted debug output.
- `AzureKms::new` chooses credential mode in priority order: embedded certificate, certificate file, then client secret.
- `AzureKms::new_with_credentials` creates both Azure `KeyClient`s and transfers config into the runtime struct.
- `generate_data_key` calls HSM `get_random_bytes` for 32 bytes, then Key Vault `encrypt` with RSA-OAEP-256, returning `DataKeyPair`.
- `decrypt_data_key` calls Key Vault `decrypt` with RSA-OAEP-256 and returns plaintext bytes.
- `convert_azure_error` normalizes Azure SDK errors into `cloud::Error::KmsError(KmsError::Other(...))`.

## Control Flow
Construction asserts `config.azure` exists, unwraps Azure settings, and requires at least one credential source. Runtime generation obtains random material from Managed HSM, encrypts it under `current_key_id`, and wraps the result in shared KMS key types. Decryption sends encrypted key bytes to Key Vault. Both paths map Azure SDK errors through `convert_azure_error`.

## State And Persistence Behavior
No TiKV state is persisted locally. Remote persistent state is the Azure Key Vault key and Managed HSM resources configured outside TiKV. `AzureKms` keeps client objects and immutable IDs/URLs for repeated calls. Plaintext key data remains in memory and `PlainKey` debug redacts it.

## Dependencies And Integration Points
The module integrates `azure_security_keyvault`, `azure_identity`, `azure_core::auth::TokenCredential`, and the local certificate credential extension. Shared KMS types come from `cloud::kms`; errors use `cloud::error`; provider name reuses `STORAGE_VENDOR_NAME_AZURE`.

## Risks And Edge Cases
Wrong-key/auth failures are not distinguished from other Azure failures because `convert_azure_error` always yields `KmsError::Other`. Misuse can panic via `assert!(config.azure.is_some())`. URL/key validation is deferred to Azure client/API calls. RSA-OAEP-256 is hard-coded, with a TODO noting algorithm choice remains open.

## Test Signals
`test_init_azure_kms` verifies missing credential failure and successful construction with client secret. The async `test_azure_kms` is effectively a manual end-to-end placeholder and active tests do not exercise network calls, error mapping, or certificate credentials.
