# sources/object-store/rustfs/crates/trusted-proxies/tests/unit/validator_tests.rs

Purpose: Unit tests for legacy `ProxyValidator`, `ProxyChainAnalyzer`, and `ClientInfo`.

Important APIs tested: `ClientInfo::direct`, `ProxyValidator::parse_x_forwarded_for`, `ProxyChainAnalyzer::analyze_chain`, `ProxyValidator::with_cache_config`, `validate_request`, and `cache_stats`.

Control flow: A helper config trusts one single IP and `10.0.0.0/8`. Tests check direct info, XFF parsing count, hop-by-hop analysis success, chain-too-long error shape, positive cache insertion for trusted peer, no negative caching for untrusted peer, and cache bypass for missing or unspecified peer.

State and dependencies: Pure unit tests with in-memory cache; no env mutation. Uses `HeaderMap`, `IpAddr`, `SocketAddr`, and crate public APIs.

Integration points: Exercises the validator used by legacy middleware/global path.

Risks and coverage gaps: Does not assert RFC7239 parsing, forwarded host/proto extraction, strict/lenient semantics, malformed header errors, continuity failure, metrics, or cache maintenance task behavior.
