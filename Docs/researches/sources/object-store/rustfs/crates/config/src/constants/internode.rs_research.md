<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/internode.rs -->
# sources/object-store/rustfs/crates/config/src/constants/internode.rs

## Purpose
Defines internode gRPC timeout, keepalive, request timeout, and data-plane transport backend constants.

## Important APIs, types, and functions
Exports connect timeout, TCP keepalive, HTTP/2 keepalive interval/timeout, RPC timeout env names and defaults, plus `ENV_RUSTFS_INTERNODE_DATA_TRANSPORT`, default backend `tcp-http`, legacy alias `tcp`, and `KNOWN_INTERNODE_DATA_TRANSPORT_BACKENDS`.

## Control flow
No runtime logic beyond tests that assert bounds and env-name stability.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Consumed by internode client/channel builders and transport selection code for distributed object-store communication.

## Risks and edge cases
Timeout defaults are low and may need high-latency tuning. The backend allow-list must stay synchronized with actual transport implementations; accepting a backend here that has no runtime implementation would fail later.

## Test signals
Unit tests pin default timeout values, env names, default transport, legacy alias, and known backend list. Integration tests should verify channel construction and request timeout behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/internode.rs -->
