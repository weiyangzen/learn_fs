# sources/object-store/rustfs/crates/trusted-proxies/src/proxy/validator.rs

Purpose: Core legacy request validator that decides whether a request came through a trusted proxy and extracts verified client metadata.

Important APIs/state: `ClientInfo::direct` and `from_trusted_proxy`; `ProxyValidator::new`, `with_cache_config`, `validate_request`, `cache_stats`, `parse_x_forwarded_for`, and crate-private `spawn_cache_maintenance_task`. The validator owns config, a `ProxyChainAnalyzer`, an `Arc<IpValidationCache>`, and optional metrics.

Control flow: `validate_request` wraps internal validation with attempt/result metrics. Internal validation handles missing/unspecified peer as direct, checks direct peer trust through positive-only cache, then either validates trusted proxy headers or returns direct info. Trusted proxy validation prefers RFC7239 when enabled, falls back to legacy X-Forwarded headers, runs chain analysis, enforces hop/continuity, and builds `ClientInfo`.

Dependencies and integration: Used by legacy layer/service/global path. It depends on `HeaderMap`, `CacheConfig`, `ProxyChainAnalyzer`, `ProxyMetrics`, and `ProxyError`.

Risks and tests: Header parsing is intentionally permissive and does not sanitize forwarded host/proto. Legacy `parse_x_forwarded_for` splits non-bracketed values at the first colon, so bare IPv6 addresses without brackets are misparsed. RFC7239 parser handles only the first comma-separated entry. Unit tests cover direct info, XFF count, hop-by-hop chain, chain-too-long, cache behavior, and cache bypass for missing/unspecified peers.
