# sources/object-store/rustfs/crates/trusted-proxies/src/error/config.rs

Purpose: Defines configuration-specific errors for the trusted proxy system.

Important APIs: `ConfigError` enum variants for missing env vars, parse failures, invalid values/IPs, validation failures, conflicts, file errors, and general invalid config. Includes conversions from `AddrParseError` and `ipnetwork::IpNetworkError`, plus helper constructors `missing_env_var`, `env_parse`, and `invalid_value`.

Control flow and state: Error type only; no runtime state. `thiserror` derives display messages used in logs and API responses via `AppError`.

Dependencies and integration: Used by config parsing and `ValidationMode::FromStr`, converted into `AppError::Config` by `error/mod.rs`.

Risks and tests: Many variants are not exercised in requested tests. Loader helper behavior currently logs some parse errors instead of returning this error type, so callers may see fewer `ConfigError`s than the type suggests.
