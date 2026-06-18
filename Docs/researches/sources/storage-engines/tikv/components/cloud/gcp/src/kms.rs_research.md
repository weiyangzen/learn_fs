# sources/storage-engines/tikv/components/cloud/gcp/src/kms.rs

## Purpose
Implements legacy GCP Cloud KMS as a `KmsProvider` using hand-built JSON REST calls through `GcpClient`. It generates HSM random bytes, encrypts them with a configured CryptoKey, and decrypts encrypted data keys.

## Important APIs, Types, And Functions
- `GcpKms` stores shared KMS `Config`, parsed location prefix, and `GcpClient`.
- `GcpKms::new` validates key ID with a regex, normalizes one trailing slash, derives `projects/.../locations/...`, and loads optional credential files.
- `do_json_request` serializes request JSON, sends POST to `https://cloudkms.googleapis.com/v1/{key}:method?alt=json`, records metrics, buffers the response, and deserializes it.
- `generate_data_key` calls `generateRandomBytes`, validates CRC32C, calls `encrypt`, validates CRC32C, and returns `DataKeyPair`.
- `decrypt_data_key` sends ciphertext with CRC32C and validates returned plaintext CRC32C.
- `serde_base64_bytes` and `Crc32Error` provide byte encoding and retryable integrity failures.

## Control Flow
Construction rejects keys outside `projects/{project}/locations/{location}/keyRings/{ring}/cryptoKeys/{key}` and strips one trailing slash. Generation makes two KMS calls: random bytes at the location resource, then encryption at the key resource. Decryption makes one KMS call at the key resource. All REST calls use Cloud Platform OAuth scope.

## State And Persistence Behavior
The provider keeps immutable config and a reusable HTTP/auth client. It persists no local state. Remote KMS keys and ciphertext are controlled by GCP Cloud KMS; plaintext only lives in memory.

## Dependencies And Integration Points
Uses `cloud::kms`, `cloud::metrics`, `GcpClient`, `hyper`, `tame_gcs` error wrappers, `serde`, `base64`, `crc32c`, `regex`, and `lazy_static`. It is exported by the legacy GCP crate root.

## Risks And Edge Cases
HTTP/KMS failures are wrapped as `KmsError::Other`, so auth/wrong-key distinction is weaker than `gcp_v2`. `serde_json::to_string(...).unwrap()` assumes request serialization cannot fail. Response bodies are fully buffered. Missing CRC fields fail deserialization rather than a dedicated CRC error.

## Test Signals
Unit tests cover invalid/valid key IDs, trailing slash normalization, location extraction, and base64 byte serde including non-ASCII bytes. No tests mock REST generate/decrypt control flow or error mapping.
