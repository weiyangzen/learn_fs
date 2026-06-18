## sources/object-store/rustfs/crates/targets/src/runtime/tls/validate.rs

Purpose: provides target-side validation helpers for CA files and client certificate/key pairs before rebuilding target TLS material.

Important APIs/types/functions: `validate_cert_key_pairing(cert_path, key_path)` allows both paths empty, rejects only-one-present, and uses `rustfs_tls_runtime::load_certs` plus `load_private_key` to parse both files. `validate_ca_file(ca_path)` allows empty CA and parses non-empty paths. `validate_tls_material(ca_path, cert_path, key_path)` composes both checks.

Control flow and state: pure synchronous validation with no persistent state. All parse failures are converted into `TargetError::Configuration` messages that name the invalid path.

Dependencies and integration points: called by `reload_target_once` before target-specific validation and material construction. It reuses shared TLS runtime PEM parsing, keeping target validation aligned with server/global TLS parsing.

Risks: validates parseability and presence pairing, but not semantic certificate/key matching, expiration, CA trust policy, or hostname constraints. Synchronous filesystem reads in shared helpers occur inside the async coordinator path and may briefly block a Tokio worker.

Test signals: no direct tests in this file; coordinator tests exercise empty-path success and target-specific validation failure. Certificate parse failure coverage appears in `tls-runtime` cert tests.
