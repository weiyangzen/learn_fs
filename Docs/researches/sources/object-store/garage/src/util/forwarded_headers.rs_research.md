<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/forwarded_headers.rs -->
# sources/object-store/garage/src/util/forwarded_headers.rs

## Purpose
Extracts a client IP address from HTTP forwarding headers for request logging.

## Important APIs, types, and functions
`handle_forwarded_for_headers(headers)` reads `X-Forwarded-For`, parses the first comma-separated IP, and returns it as a string.

## Control flow
The function rejects missing headers, invalid UTF-8, empty first values, and invalid IP syntax through Garage `Error`. Tests cover IPv4, IPv6, invalid IPs, and missing headers.

## State and persistence behavior
No state or persistence. The result affects logs and metrics context, not authorization.

## Dependencies and integration points
Used by Garage web request logging and likely other HTTP endpoints behind proxies. Depends on `hyper::HeaderMap` and `std::net::IpAddr` parsing.

## Risks and test signals
`X-Forwarded-For` is client-controlled unless a trusted proxy strips/sets it; code should not use this for security decisions. Existing tests validate parsing behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/forwarded_headers.rs -->
