## sources/object-store/rustfs/crates/tls-runtime/src/debug.rs

Purpose: defines serializable debug/status response structures for TLS runtime observability.

Important APIs/types/functions: `TlsConsumerStatusItem` records a consumer name, generation, root CA presence, and mTLS identity presence. `TlsDebugStatusResponse` contains a foundation `TlsRuntimeStatusSnapshot` plus consumer status items. `TlsDebugStatusResponse::builder` creates `TlsDebugStatusResponseBuilder`; `push_consumers` appends iterable consumer status entries; `build` returns the response.

Control flow and state: builder is immutable-by-value and only accumulates a vector before build. No global state.

Dependencies and integration points: depends on serde and `TlsRuntimeStatusSnapshot`. Intended for admin/debug endpoints that combine foundation runtime and consumer-specific status.

Risks: `consumer` is `&'static str`, so dynamic consumer labels require static identifiers or a type change. The response reports presence booleans rather than detailed certificate metadata, which is safer but less diagnostic.

Test signals: unit test serializes a built response to JSON and verifies `foundation` and array `consumers` fields exist.
