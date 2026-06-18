## sources/object-store/rustfs/crates/tls-runtime/src/server.rs

Purpose: implements a reloadable rustls server certificate resolver that can serve SNI-specific certificates, fall back to a default certificate, and reload material from a TLS source directory on a poll loop.

Important APIs/types/functions: private `ResolverState` holds `ResolvesServerCertUsingSni`, optional default `CertifiedKey`, cert count, and fingerprint. `ReloadableServerCertResolver` owns `TlsSource`, current resolver state behind `std::sync::RwLock`, and an atomic generation. `load_from_source`/`load_from_directory` build initial state. `reload` reloads certs, compares fingerprints, swaps resolver state, and increments generation. It implements rustls `ResolvesServerCert`. `spawn_server_cert_reload_loop(protocol, resolver, options, shutdown_rx)` polls reload until a watch shutdown signal.

Control flow and state: domain entries are sorted before fingerprinting and resolver construction. `reload` handles poisoned locks by taking the inner value and still proceeding. The server resolver's `resolve` method performs a read lock and tries SNI first, then default cert.

Dependencies and integration points: uses cert directory loading, `TlsReloadOptions`, metrics, rustls server traits/signing, Tokio watch/time, and tracing. Intended for HTTP/S3/admin server TLS hot reload.

Risks: synchronous reload and resolver-state construction happen inside async poll task. Generation uses relaxed atomics and `fetch_add` without saturation. `spawn_server_cert_reload_loop` ignores detect mode and starts whenever enabled, unlike the foundation coordinator. Resolver reload failure keeps old state but only logs/metrics the error.

Test signals: tests verify default cert replacement after file rotation, unchanged reload skip, and stable fingerprint across domain ordering.
