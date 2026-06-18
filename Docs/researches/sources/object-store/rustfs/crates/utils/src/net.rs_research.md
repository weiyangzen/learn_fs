# sources/object-store/rustfs/crates/utils/src/net.rs

## Purpose
Provides network utility functions for local address validation, hostname resolution, endpoint URL construction, available-port discovery, stream truncation, and host display/parsing.

## Important APIs, Types, And Functions
`is_socket_addr` validates IP/socket strings, including scoped IPv6 zone identifiers. `check_local_server_addr`, `is_local_host`, `must_get_local_ips`, `get_host_ip`, `parse_and_resolve_address`, and `get_available_port` support bind/listen address validation. `get_endpoint_url`, `get_default_location`, and `is_custom_query_value` support S3 endpoint/query handling. `XHost` stores a resolved host name, port, and port-set flag, with `Display` and `TryFrom<String>`. `bytes_stream` truncates an async bytes stream to a declared content length.

## Control Flow And State
`LOCAL_IPS` is a process-global lazy snapshot from `must_get_local_ips` with loopback fallback. DNS resolution uses a global `DNS_CACHE` with five-minute TTL and a test-only custom resolver behind `RwLock`. `get_host_ip` checks the cache for domains, resolves, caches up to about 1000 entries, and logs misses/errors. `parse_and_resolve_address` treats `:port` as IPv6 unspecified bind and replaces port zero with an ephemeral port. `bytes_stream` decreases a remaining counter and truncates oversized chunks.

## Dependencies And Integration Points
Uses `bytes`, `futures`, `transform_stream`, `url`, `netif`, standard sockets, and `tracing`. It is exported under the `net` feature and is central to server startup validation and network-aware endpoint behavior.

## Risks And Test Signals
`LOCAL_IPS` is fixed after first access, so interface changes are not reflected. `get_available_port` has an inherent race after releasing the listener. `bytes_stream` can underflow if the stream continues after remaining reaches zero and a nonempty chunk is seen. Domain resolution tests use a mock resolver with a global lock; other tests still depend on local interfaces and localhost resolution. Unit tests cover socket parsing, local host checks, DNS mock paths, XHost formatting/parsing, bind parsing, and IPv6 zones.
