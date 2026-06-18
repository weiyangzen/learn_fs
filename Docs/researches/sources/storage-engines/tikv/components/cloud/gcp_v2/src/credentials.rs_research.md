# sources/storage-engines/tikv/components/cloud/gcp_v2/src/credentials.rs

## Purpose
Centralizes GCP v2 credential handling and rustls crypto-provider initialization. It supports default credentials, JSON service-account credentials, JSON external-account credentials, and FIPS/non-FIPS rustls provider setup.

## Important APIs, Types, And Functions
- `CredentialsMode` is either `Default` or `Json(String)`; `Debug` redacts JSON.
- `validate_credentials_json` ensures credential blobs are syntactically valid JSON.
- `ensure_default_rustls_provider` installs or validates a process-global rustls provider. Under `fips`, it requires aws-lc-rs FIPS; otherwise it installs ring.
- `build_credentials` parses JSON, checks `type`, and builds `google_cloud_auth::credentials::Credentials` for `service_account` or `external_account`; default mode returns `None`.

## Control Flow
Callers validate credentials synchronously during config parsing but defer `build_credentials` until async client initialization to avoid `tokio::spawn` from non-Tokio threads. Rustls provider setup is idempotent if an acceptable provider is installed and errors if an incompatible provider was installed first.

## State And Persistence Behavior
Credential JSON is held in memory inside `CredentialsMode::Json`. Rustls provider state is process-global. The module reads no files itself; callers read files before creating `CredentialsMode`.

## Dependencies And Integration Points
Used by `gcp_v2::GcsStorage` and `gcp_v2::GcpKms`. Depends on `google_cloud_auth`, `serde_json`, and `rustls`.

## Risks And Edge Cases
Only `service_account` and `external_account` JSON credential types are supported; authorized-user credentials supported by legacy `gcp` are rejected. Rustls provider initialization is global and can fail if another provider was installed first. JSON syntax validation is separate from semantic credential validation.

## Test Signals
`test_ensure_default_rustls_provider` verifies idempotent provider setup and FIPS flag matching. KMS tests also verify external-account JSON is recognized instead of rejected as unsupported.
