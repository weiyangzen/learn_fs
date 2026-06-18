# sources/object-store/garage/src/net/util.rs

Purpose: small utilities for NetApp serialization, shutdown signaling, and peer address parsing/resolution.

Important APIs and functions: `rmp_to_vec_all_named` serializes arbitrary Serde values to MessagePack with struct-map field names. `await_exit` blocks until a `watch::Receiver<bool>` observes `true` or the sender closes. `watch_ctrl_c` returns a cancellation receiver driven by `tokio::signal::ctrl_c`. `parse_peer_addr`, `parse_and_resolve_peer_addr`, and `parse_and_resolve_peer_addr_async` parse `<public key hex>@<host>:<port>` forms into `NodeID` plus socket addresses.

Control flow: `await_exit` repeatedly checks `borrow_and_update` and awaits `changed`. The parsers split at `@`, hex-decode the full public key, convert it to `NodeID`, then parse or resolve the host suffix. The async resolver delegates to `tokio::net::lookup_host`; the sync resolver uses `ToSocketAddrs`.

State and persistence: no persistence. `watch_ctrl_c` spawns one task and owns the sending side of a watch channel.

Dependencies and integration: used by client/server loops, system bootstrap peer resolution, endpoint serialization, and command-line peer specs. It depends on `rmp-serde`, `hex`, Tokio watch/signal, and Garage `NodeID`.

Risks and test signals: parser errors collapse to `None`, so callers need good diagnostics. Host resolution can return multiple addresses and callers decide retry order. `watch_ctrl_c` unwraps send and signal setup, appropriate for process-level shutdown but not for library isolation. No direct unit tests here.
