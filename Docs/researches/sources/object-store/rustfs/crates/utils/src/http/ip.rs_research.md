# sources/object-store/rustfs/crates/utils/src/http/ip.rs

## Purpose
Extracts client source IP and scheme from reverse-proxy headers. It supports de-facto `X-Forwarded-*` and `X-Real-IP` headers plus RFC 7239 `Forwarded`.

## Important APIs, Types, And Functions
Constants define `x-forwarded-for`, `x-forwarded-proto`, `x-forwarded-scheme`, and `x-real-ip`. `get_source_scheme` checks `X-Forwarded-Proto`, `X-Forwarded-Scheme`, then parses `Forwarded` for `proto=http|https`. `get_source_ip_from_headers` checks `X-Forwarded-For` when `_RUSTFS_API_XFF_HEADER` is `on`, falls back to `X-Real-IP`, then `Forwarded for=...`. `get_source_ip_raw` falls back to `remote_addr` and strips socket ports when possible. `get_source_ip` brackets IPv6-like results.

## Control Flow And State
Two `LazyLock<Regex>` values parse `Forwarded` fields. The only external state is `_RUSTFS_API_XFF_HEADER`, defaulting to enabled. The XFF parser only splits on comma-space, not a bare comma, and the Forwarded parser extracts the first `for=` value.

## Dependencies And Integration Points
Depends on `http::HeaderMap`, `regex`, `std::env`, and socket parsing. This module is re-exported via `http/mod.rs` for request logging, auditing, policy, or API handlers that need client identity behind proxies.

## Risks And Test Signals
Trusting forwarded headers is security-sensitive; correctness depends on deployment-level trusted proxy controls. XFF comma parsing may retain multiple values if proxies emit `a,b` without a space. Unit tests cover basic scheme/IP extraction, remote fallback parsing, and IPv6 bracketing but not disabled XFF, malformed Forwarded forms, or proxy trust boundaries.
