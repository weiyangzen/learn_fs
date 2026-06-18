# sources/object-store/rustfs/crates/kms/src/config.rs

## Purpose
Defines KMS runtime configuration, backend selection, secure defaults, redaction rules, and environment loading. It is the policy gate for whether local/Vault development defaults are allowed.

## Important APIs, Types, And Functions
`KmsBackend` selects `Local`, `VaultKV2`/legacy `Vault`, or `VaultTransit`. `KmsConfig` carries backend config, default key id, timeout, retry count, cache settings, and `allow_insecure_dev_defaults`. `BackendConfig` wraps `LocalConfig`, `VaultConfig`, and `VaultTransitConfig`. `VaultAuthMethod` supports token and AppRole. `TlsConfig` captures Vault TLS paths and `skip_verify`. `CacheConfig` controls key metadata cache sizing.

Constructors include `KmsConfig::local`, `vault`, `vault_approle`, and `vault_transit`, plus builder helpers for default key, insecure development mode, timeout, and caching. `from_env` reads `RUSTFS_KMS_*` variables, builds backend-specific config, and calls `validate`. `KMS_CONFIG_REDACTION_RULES`, custom `Debug` implementations, and `redacted_secret*` avoid leaking secret material in diagnostics.

## Control Flow
`validate` checks timeout and retry count first, then validates backend-specific invariants. Local mode requires an absolute key directory; outside explicit development mode it also requires a non-empty master key and rejects temp-directory storage. Vault modes require HTTP(S) scheme, non-empty mount path, and outside development mode reject HTTP, the default `dev-token`, and TLS verification skipping. HTTPS without custom TLS config is logged as a warning rather than rejected.

`from_env` starts from `Default`, parses backend, default key, timeout, retry attempts, cache toggle, and the development opt-in flag, then replaces `backend_config` with the selected backend's env-derived config. It fails closed through `validate`.

## State And Persistence
All config structs derive serde serialization/deserialization, so this file defines the persisted shape for KMS service configuration. Secrets are serialized for persistence but redacted only in debug output and by the security governance redaction rule list. `Duration` fields are serialized using serde's standard representation for the type.

## Dependencies And Integration
Uses `rustfs_utils` env helpers, `rustfs_security_governance` redaction rules, `serde`, `url`, `PathBuf`, and `tracing`. `service_manager.rs` validates `KmsConfig` before accepting or starting a service. Backend constructors consume `BackendConfig`.

## Risks And Edge Cases
The default local config is intentionally invalid for production because it lacks a master key and uses a temp directory. `from_env` default local key dir is relative, which also fails validation unless callers provide an absolute path. Vault token auth is the only env path; AppRole must be configured programmatically or by deserializing config. TLS `client_key_path` is not validated alongside `client_cert_path`, so invalid mTLS combinations may fail later in backend setup.

## Test Signals
Tests cover default config fail-closed behavior, local and Vault dev-default opt-in, Vault Transit config, legacy Vault serde aliases, redaction rule validity, debug redaction without breaking persistence, env parsing, and skip-TLS rejection without the explicit development flag.
