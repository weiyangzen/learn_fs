# sources/storage-engines/tikv/components/cloud/gcp_v2/src/kms.rs

## Purpose
Implements GCP Cloud KMS using the generated `google-cloud-kms-v1` client. It replaces hand-built REST KMS with richer error mapping, lazy async client construction, CRC32C checks, custom endpoints, and external-account credentials.

## Important APIs, Types, And Functions
- `GcpKms` stores shared KMS config, parsed location, optional endpoint, credential mode, and a `OnceCell<KeyManagementService>`.
- `GcpKms::new` validates GCP config, ensures rustls provider, strips trailing key-id slash, parses the key id, reads optional credential file as UTF-8 JSON, validates it, and stores `CredentialsMode`.
- `get_client` lazily builds the generated KMS client with optional endpoint and credentials.
- `map_kms_call_error` maps unauthenticated/permission-denied gRPC or HTTP 401/403 to `WrongMasterKey`.
- `generate_data_key` calls `generate_random_bytes` with HSM protection, checks data CRC32C, encrypts with plaintext CRC32C, verifies `verified_plaintext_crc32c`, checks ciphertext CRC32C, and returns `DataKeyPair`.
- `decrypt_data_key` sends ciphertext and CRC32C, checks plaintext CRC32C, and returns plaintext bytes.

## Control Flow
Construction performs static validation and defers network/client work until first KMS call. The first call initializes the client in `OnceCell`; later calls clone the generated client handle. Generation validates random bytes, encryption verification, and ciphertext integrity. Decrypt performs one service call followed by integrity validation.

## State And Persistence Behavior
`GcpKms` persists no local data beyond cached client/config/credential JSON. Remote KMS state is the configured CryptoKey. Plaintext key bytes live only in memory and are wrapped in `PlainKey` for redacted debug output.

## Dependencies And Integration Points
Uses `cloud::kms`, `cloud::metrics`, `google_cloud_kms_v1`, `google_cloud_gax`, `bytes`, `crc32c`, `tokio::sync::OnceCell`, and local credentials helpers. Exported from `gcp_v2::lib`.

## Risks And Edge Cases
`parse_key_id` requires exactly eight slash-separated components and rejects key version names. `check_crc32` casts optional `i64` to `u32`; negative service values would wrap, though Google APIs should not produce them. Missing CRC fields and failed plaintext verification are retryable `Other` errors. Metrics labels use cloud `"gcp"` although provider name is `"gcp_v2"`.

## Test Signals
Unit tests use generated KMS stubs for roundtrip generate/decrypt and metrics increments, verify permission-denied maps to `WrongMasterKey`, check external-account credentials are accepted, and ensure custom endpoint without credentials stays in default credential mode.
