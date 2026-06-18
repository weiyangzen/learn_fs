<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/socket_address.rs -->
# sources/object-store/garage/src/util/socket_address.rs

## Purpose
Configuration type accepting either TCP socket addresses or Unix socket paths for Garage HTTP-style listeners.

## Important APIs, types, and functions
`UnixOrTCPSocketAddress::{TCPSocket, UnixSocket}` implements `Display` and custom serde `Deserialize`.

## Control flow
Deserialization treats strings starting with `/` as Unix socket paths and all others as `SocketAddr`. Display renders `http://addr` or `http+unix://path`.

## State and persistence behavior
No runtime state. Parsed values drive listener binding in API/web/admin servers.

## Dependencies and integration points
Used by `Config`, `WebServer`, and common server setup. Depends on serde, `SocketAddr`, `PathBuf`, and `FromStr`.

## Risks and test signals
Relative Unix socket paths are not accepted by the leading-slash heuristic. IPv6/TCP parse errors surface as config errors. Tests should cover IPv4, IPv6, Unix paths, and malformed strings.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/socket_address.rs -->
