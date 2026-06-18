# sources/object-store/rustfs/crates/kms/examples/kms_vault_kv_demo.rs

## Purpose
`kms_vault_kv_demo.rs` is an executable walkthrough for the Vault KV2-backed KMS configuration. It demonstrates using Vault as persistent key storage while exercising the same high-level encryption workflow as the local demo.

## Important APIs, Types, and Functions
It uses the same public KMS API types as the local demo plus `KmsError` and `url::Url`. Vault address is read from `RUSTFS_KMS_VAULT_ADDRESS` with a localhost default, and the token is read from `RUSTFS_KMS_VAULT_TOKEN` with a development fallback of `dev-token`. Configuration uses `KmsConfig::vault(vault_url, vault_token).with_default_key(...).with_cache(true)`.

## Control Flow
The demo initializes and configures the global KMS service with Vault, starts it, obtains the global encryption service, tries to describe a fixed master key, creates it if `KmsError::KeyNotFound` occurs, describes it again, optionally generates a data key, encrypts and decrypts object data, verifies round-trip equality, lists keys, prints cache stats, checks Vault health, stops the service, and prints Vault inspection tips.

## State and Persistence Behavior
Keys persist in Vault under the configured KV path. The fixed key ID `demo-key-master-1` is reused across runs, so the example handles existing keys. Process-local cache is enabled. No local files are written by this example except normal build/runtime outputs.

## Dependencies and Integration Points
The example integrates with a running Vault server, Vault token auth, the global KMS manager, and the object encryption service. It demonstrates error-specific handling for `KeyNotFound`.

## Risks and Edge Cases
The default token `dev-token` and localhost Vault address are development-oriented. Production use requires a real token and TLS/auth hardening. The example assumes the Vault backend supports the high-level object flow; it does not validate Vault mount setup beyond health/key operations. The final tips mention paths under `secret/rustfs/kms/keys`, matching KV2 storage assumptions rather than the dedicated Transit backend.

## Test Signals
This is a manual smoke/demo program. It gives practical integration guidance but no automated assertion beyond plaintext/decrypted equality during execution.
