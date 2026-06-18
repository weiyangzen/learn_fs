## sources/object-store/rustfs/crates/tls-runtime/src/state.rs

Purpose: defines shared TLS runtime generation, published state, atomic runtime state, and serializable status snapshot structures.

Important APIs/types/functions: `TlsGeneration(pub u64)`, `TlsPublishedState<M>` with generation/material/fingerprint/load time, and `TlsReloadRuntimeState<M>` with `current`, `last_good`, attempt/success atomics, and async `last_error`. Methods include `new`, `current_generation`, `bump_generation`, `mark_attempt`, `mark_success`, and timestamp getters. `TlsRuntimeStatusSnapshot` groups runtime, outbound, server, and consumer sections; `from_outbound_only` builds a reduced status; `is_complete` reports whether any server/outbound material exists. `detect_mode_label` maps enum to static strings.

Control flow and state: `ArcSwap` gives lock-free reads of current and last-good states. `bump_generation` saturates at `u64::MAX`. Timestamp atomics use relaxed ordering in this shared state. `last_error` is an async `tokio::sync::RwLock`.

Dependencies and integration points: used by shared coordinator, debug responses, outbound-only status, and tests. Serde derives make status snapshots admin/API friendly.

Risks: relaxed atomics are likely fine for observability timestamps but not synchronization. Like target state, generation bump is separate from publication and assumes one publisher at a time. Status exposes source paths and only coarse material booleans.

Test signals: tests cover generation/timestamp tracking, generation saturation, status completeness when roots exist, and incompleteness when empty.
