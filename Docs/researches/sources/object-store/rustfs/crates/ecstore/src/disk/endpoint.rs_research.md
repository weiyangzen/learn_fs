# sources/object-store/rustfs/crates/ecstore/src/disk/endpoint.rs

## Purpose
`endpoint.rs` defines RustFS disk endpoints as either local filesystem paths or HTTP(S) URL endpoints. It normalizes path/url input, rejects unsupported endpoint forms, tracks whether URL endpoints resolve to the local server, and exposes host/path helpers used by setup, local disk creation, remote RPC routing, and notification paths.

## Important APIs, Types, And Functions
- `EndpointType` distinguishes `Path` endpoints backed by `file://` URLs from remote-style `Url` endpoints.
- `Endpoint` stores the parsed `Url`, `is_local`, and pool/set/disk indices. The indices start at `-1` and are populated by the endpoint layout code.
- `impl TryFrom<&str> for Endpoint` performs validation and normalization for both local paths and URL endpoints.
- `Endpoint::get_type`, `set_pool_index`, `set_set_index`, and `set_disk_index` provide layout metadata.
- `Endpoint::update_is_local` calls `rustfs_utils::is_local_host` for URL endpoints to decide if the target host/port is local.
- `grid_host` returns scheme plus host and optional port for grid/RPC clients, while `host_port` omits the scheme for uniqueness and host matching.
- `get_file_path` decodes the URL path and, on Windows, strips the leading slash from `file://` drive paths.
- `url_parse_from_file_path` converts local paths to `file://` URLs and rejects socket-address-looking values without a scheme.

## Control Flow
Parsing rejects empty, root slash, and root backslash endpoints up front. If `Url::parse` succeeds with a host, the endpoint must be `http` or `https`, must not have username, fragment, or query, and must have a non-root path. Non-Windows URL paths are absolutized before being written back to the URL. Windows has special handling for `/C:/...` URL paths so actual drive paths are not mistaken for relative current-drive paths.

If `Url::parse` succeeds without a host, or fails with `RelativeUrlWithoutBase`, the value is treated as a local path and passed to `url_parse_from_file_path`. If parsing fails due to invalid port or empty host, user-facing error messages are specialized. `url_parse_from_file_path` first checks whether the pre-slash prefix resembles a socket address; if so, it refuses it as a missing-scheme URL rather than silently creating a local path.

Display is intentionally asymmetric: `file://` endpoints display as decoded local file paths, while URL endpoints display as URL strings. This matches user-facing endpoint config and logging expectations.

## State And Persistence Behavior
This file does not persist data. It constructs normalized endpoint values that later become durable identity context in format layouts and runtime maps. The pool/set/disk indices are mutable fields on the endpoint instance and are used as metric labels and layout identity in other modules.

Path normalization can affect persisted or compared values indirectly: local paths are absolutized, spaces and special characters are percent-encoded internally, and `get_file_path` decodes them when passed to local disk code.

## Dependencies And Integration Points
`Endpoint` is consumed by `endpoints.rs` for server layout parsing, setup-type inference, local-path uniqueness, remote host grouping, and grid host construction. `disk/local.rs` uses `get_file_path` to create local disk roots. `rpc/remote_disk.rs` uses `grid_host`, `host_port`, and `get_file_path` for remote disk behavior. `sets.rs`, `store/peer.rs`, `notification_sys.rs`, and tests throughout ecstore compare endpoint hosts and local paths. Metrics in `health_state.rs` and `disk_store.rs` use endpoint display plus indices as labels.

The module depends on `path_absolutize` for normalization, `url` for parsing and `file://` conversion, `urlencoding` for decoded file-path presentation, and `rustfs_utils::{is_local_host,is_socket_addr}` for host classification.

## Risks And Edge Cases
- Absolutizing URL paths means configured remote paths may be normalized according to the local platform, which is intentional but can surprise when comparing configs across OSes.
- The `http://server:/path` case parses as a URL without a numeric port and is accepted by tests. Callers relying on explicit port validation must handle that elsewhere.
- `get_file_path` for URL endpoints returns only the URL path; it is useful for remote disk path fields but should not be confused with a local filesystem path unless `is_local` and endpoint type are considered.
- The socket-address heuristic in `url_parse_from_file_path` only checks the prefix before `/`; unusual path names that resemble `host:port` can be rejected.
- Windows path parsing has separate fallback code and synthetic leading slash handling; regressions here can break local endpoints on Windows even if Unix tests pass.

## Test Signals
Tests cover path and URL endpoint creation, empty/root rejection, unsupported schemes, URL query rejection, empty host and invalid port errors, root URL path rejection, missing scheme for socket addresses, display formatting, type detection, pool/set/disk index setters, `grid_host`, `host_port`, decoded `get_file_path`, Windows drive URL behavior, clone/equality/hash behavior, paths with spaces and special characters, percent-encoding round trips, `update_is_local`, and file-path URL conversion.
