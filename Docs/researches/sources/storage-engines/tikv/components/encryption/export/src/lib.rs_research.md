# sources/storage-engines/tikv/components/encryption/export/src/lib.rs

Purpose: This crate-level library reexports core encryption APIs and provides factory functions that turn TiKV encryption configuration into concrete local, plaintext, or cloud KMS master-key backends.

Important APIs and functions: Public functions are `data_key_manager_from_config`, `create_async_backend`, `create_backend`, and `create_cloud_backend`. Internal helpers `create_backend_inner` and `create_async_backend_inner` dispatch on `MasterKeyConfig`. The crate reexports `AsyncBackend`, `Backend`, `DataKeyManager`, `DataKeyManagerArgs`, config types, cleanup helpers, `Iv`, `KmsBackend`, and error/result types.

Control flow: Backend creation logs failures and propagates errors. `create_cloud_backend` converts `KmsConfig` into `cloud::Config`, logs region/endpoint/key/vendor, then dispatches AWS/default, Azure, GCP, or GCP v2 providers with provider-specific sanity checks. `data_key_manager_from_config` builds current and lazy previous master-key backends for `DataKeyManager::new`.

State and persistence behavior: The library itself stores no state, but returned backends may read key files or call external KMS services. `DataKeyManager` persists/uses the file dictionary at the supplied dictionary path.

Dependencies and integration points: It connects core encryption to `aws`, `azure`, `gcp`, `gcp_v2`, `cloud`, and TiKV logging/error utilities.

Risks: Empty vendor defaults to AWS. Azure/GCP require provider-specific nested config; missing config returns explicit errors. Factory functions log key IDs and endpoints, which is operationally useful but should avoid secrets.

Test signals: The local test checks Azure missing-config failure and successful secure backend creation with a populated Azure config.
