# sources/object-store/rustfs/crates/protocols/src/ftps/config.rs

Purpose: This file defines FTPS startup configuration and initialization errors, including listener binding, passive ports, external passive address, TLS requirement, certificate directory, and optional CA file.

Important APIs and types: `FtpsInitError` wraps bind I/O errors, `libunftp::ServerError`, and human-readable invalid config messages. `FtpsConfig` stores `bind_addr`, `passive_ports`, `external_ip`, `ftps_required`, `tls_enabled`, `cert_dir`, and `ca_file`. `validate` and `parse_passive_ports` are the key methods; `Default` supplies `0.0.0.0:8021`, `40000-50000`, TLS enabled, and no certificate directory.

Control flow: `validate` rejects required FTPS without a certificate directory, checks certificate and CA paths with `tokio::fs::try_exists`, and validates passive-port syntax when configured. `parse_passive_ports` splits `start-end`, parses both as `u16`, and rejects reversed ranges.

State and persistence behavior: This file does not persist anything. It only reads filesystem metadata for certificate-related paths during validation.

Dependencies and integration points: `FtpsServer::new` calls `validate` before building the libunftp server. `FtpsServer::start` later consumes the passive range and certificate fields. Defaults come from crate constants.

Risks: `try_exists(...).unwrap_or(false)` intentionally treats lookup errors as missing, which simplifies startup errors but can hide permission-vs-absence distinctions. When `tls_enabled` is true but `ftps_required` is false and no cert dir is set, validation allows plain FTP fallback through server logic; operators must set both fields correctly for mandatory TLS.

Test signals: No local tests are present. Useful tests would cover missing cert dir when required, missing CA file, malformed passive ranges, start greater than end, and default parse success.
