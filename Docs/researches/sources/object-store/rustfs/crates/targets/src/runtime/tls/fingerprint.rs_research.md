## sources/object-store/rustfs/crates/targets/src/runtime/tls/fingerprint.rs

Purpose: provides target-specific TLS fingerprint and generation types used to detect CA/client certificate/client key changes for outbound target connections.

Important APIs/types/functions: `TargetTlsFingerprint` stores optional SHA256 digests for CA, client cert, and client key. `TargetTlsGeneration(pub u64)` is a saturating generation counter wrapper. `TargetTlsState` combines generation and optional fingerprint, with `refresh`, `needs_update`, and `reset`. `build_target_tls_fingerprint(ca_path, client_cert_path, client_key_path)` asynchronously reads non-empty paths and digests bytes through `rustfs_tls_runtime::TlsFingerprint::from_optional_bytes`.

Control flow and state: empty paths map to `None` digests. `TargetTlsState::refresh` mutates only when the candidate fingerprint differs, saturating generation upward and storing the new fingerprint. `needs_update` is a non-mutating gate intended for build-before-publish flows.

Dependencies and integration points: uses `tokio::fs::read`, `TargetError::Configuration`, and shared runtime fingerprint hashing. It feeds `TargetTlsReloadCoordinator` comparisons and initial state.

Risks: it reads whole files into memory; acceptable for TLS material but still unbounded by code. Error messages include paths. Reusing `TlsFingerprint::server_sha256` for each target file digest is a convenient but slightly opaque implementation detail.

Test signals: unit tests cover generation increments only on change, reset, equality when all digest fields match, and inequality on CA differences. File-read error and empty-path behavior are exercised indirectly by coordinator tests.
