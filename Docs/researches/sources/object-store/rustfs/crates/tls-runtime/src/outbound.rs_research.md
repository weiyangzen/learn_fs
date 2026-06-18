## sources/object-store/rustfs/crates/tls-runtime/src/outbound.rs

Purpose: publishes and reads global outbound TLS root CA and mTLS identity state used by outbound clients.

Important APIs/types/functions: `GlobalPublishedOutboundTlsState` captures generation, optional root CA PEM, and optional mTLS identity. `GlobalOutboundTlsStateSummary` exposes generation and presence booleans. `publish_global_outbound_tls_state(generation, material)` writes `GLOBAL_ROOT_CERT`, `GLOBAL_MTLS_IDENTITY`, and global generation. `load_global_outbound_tls_state`, `load_global_outbound_tls_generation`, and `summarize_global_outbound_tls_state` read back state.

Control flow and state: publishing clears global root cert when material has no root CA bytes, always updates mTLS identity, then sets generation and metrics. Reads acquire async global locks from `rustfs_common`.

Dependencies and integration points: integrates `TlsMaterialSnapshot` outbound material with global process-level TLS configuration consumed by outbound HTTP/database/etc. clients. Depends on `rustfs_common` global TLS storage and metrics.

Risks: process-global mutable TLS state means all outbound consumers share the same roots/identity. Callers must coordinate publication order; there is no compare-and-swap against generation. Clearing root CA on empty material is explicit and can affect all clients.

Test signals: no direct tests in this file; debug/status and coordinator tests cover related generation handling indirectly.
