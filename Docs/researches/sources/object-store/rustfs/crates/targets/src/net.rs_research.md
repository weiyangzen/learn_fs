# sources/object-store/rustfs/crates/targets/src/net.rs

## Purpose
Network and HTTP metadata helper module. It extracts request/response headers for target payloads, parses and validates hosts/URLs, normalizes URL display, and classifies common network errors.

## Important APIs, types, and functions
- `NetError` classifies invalid hosts, missing IPv6 brackets, parse failures, unexpected schemes, and URLs with schemes but empty hosts.
- `Host` represents a host name/IP plus optional port and implements display/equality helpers.
- Header helpers extract all headers, host, port, content length, referer, and user-agent from `hyper::HeaderMap` or S3 request/response types.
- `parse_host`, `trim_ipv6`, `ParsedURL`, `parse_url`, and `parse_http_url` validate host names/IPs, handle IPv6 zone IDs, infer default ports, clean paths, and normalize default ports on display.
- `is_network_or_host_down`, `is_conn_reset_err`, and `is_conn_refused_err` classify `std::io::Error` values.

## Control flow
Header extraction iterates header maps and skips non-UTF-8 values. Port detection prioritizes `x-forwarded-port`, explicit host port, forwarded-proto defaults, then a `port` header. Host parsing splits bracketed IPv6, bare IPv6, and host:port forms, validates labels with a regex, and supports zone suffixes for IP validation. URL parsing rejects `scheme:///path`, validates host/port through `parse_host`, and normalizes path components.

## State and persistence behavior
No persistent state exists. `HOST_LABEL_REGEX` is lazily initialized once through `LazyLock`.

## Dependencies and integration points
It depends on `hyper`, `s3s`, `url`, `regex`, `serde`, `libc`, and `hashbrown`. Config builders and connectivity checks use `parse_url`; target delivery code can use header extraction to build event metadata.

## Risks and edge cases
`get_request_port` treats host port `0` as absent and may infer forwarded-proto defaults instead. Path cleaning removes `..` and non-normal path components, which is useful for canonicalization but can change user-supplied URL text. Header extraction drops binary or invalid header values.

## Test signals
Tests cover port priority and IPv6 handling, host parse success/failure for IPv4, hostnames, bracketed and bare IPv6, zone IDs, invalid brackets, invalid host labels, URL default-port normalization, empty-host rejection, invalid-host rejection, and path normalization.
