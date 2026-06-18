# sources/object-store/rustfs/crates/protocols/src/webdav/config.rs

Defines WebDAV server configuration and initialization errors.

Important API surface: `WebDavInitError` distinguishes bind, server, invalid config, and TLS failures. `WebDavConfig` contains bind address, TLS enablement, certificate directory, optional CA file, maximum request body size, and request timeout. `validate()` checks TLS file requirements and nonzero limits. `Default` binds `0.0.0.0:8080`, enables TLS, and sets 5 GiB body / 300 second timeout defaults.

Validation rejects TLS-enabled configs without `cert_dir`, rejects missing certificate directories and CA files using async `tokio::fs::try_exists`, and rejects zero body size or timeout.

There is no persistence; this is runtime configuration consumed by `server.rs`. Dependencies are `SocketAddr`, `thiserror`, and Tokio filesystem checks. `WebDavServer::new()` calls `config.validate()` before accepting a config.

Risks: the default enables TLS but leaves `cert_dir` unset, so `WebDavConfig::default()` is intentionally incomplete until the caller supplies certificates or disables TLS. `ca_file` is validated but server TLS currently configures `with_no_client_auth`, so CA validation is not enforced by the server path. `request_timeout_secs` is validated but not visibly applied in `server.rs`.

No tests live here. Behavioral coverage should come from server initialization tests that exercise default, TLS, and invalid limit cases.
