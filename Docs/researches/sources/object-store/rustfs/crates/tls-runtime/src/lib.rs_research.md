## sources/object-store/rustfs/crates/tls-runtime/src/lib.rs

Purpose: defines the public API surface of the `rustfs-tls-runtime` crate by declaring modules and re-exporting TLS certificate, config, reload, debug, material, metrics, outbound, server, source, and state types.

Important APIs/types/functions: public re-exports include certificate loaders/inspectors/resolvers, reload options, `TlsReloadCoordinator`, `TlsConsumer`, debug response builders, `TlsRuntimeError`, `TlsFingerprint`, `TlsMaterialSnapshot`, metrics helpers, global outbound TLS state helpers, `ReloadableServerCertResolver`, `spawn_server_cert_reload_loop`, `TlsSource`, and runtime state/status structs.

Control flow and state: no runtime behavior beyond tests; it establishes stable import paths for downstream crates like `rustfs-targets`.

Dependencies and integration points: all crate modules are public. The targets crate imports config, fingerprint, cert loaders, and validation-related helpers through this crate.

Risks: broad re-exporting makes internal module changes observable to downstream users. The test module constructs simplified material snapshots, so it validates API wiring more than full certificate lifecycle.

Test signals: tests verify missing TLS source directories fail, server material fingerprint changes when certificate/key material changes, and the coordinator publishes initial generation 1.
