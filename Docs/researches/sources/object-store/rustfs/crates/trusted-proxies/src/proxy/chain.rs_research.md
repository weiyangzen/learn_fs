# sources/object-store/rustfs/crates/trusted-proxies/src/proxy/chain.rs

Purpose: Analyzes proxy IP chains to identify the real client and validate trust according to configured mode.

Important APIs/state: `ChainAnalysis` returns client IP, hop count, continuity, warnings, mode, and trusted suffix. `ProxyChainAnalyzer` owns `TrustedProxyConfig` and a precomputed `HashSet<IpAddr>` for single IPs and small IPv4 CIDRs (`/24` or narrower).

Control flow: `analyze_chain` validates header IPs, appends current direct proxy, enforces max hops, dispatches to lenient/strict/hop-by-hop logic, checks continuity, collects warnings, and validates the chosen client IP. Lenient trusts the full chain if the last proxy is trusted. Strict requires every IP in the chain to be trusted. Hop-by-hop walks from right to left until the first untrusted IP and treats that as the client boundary.

Dependencies and integration: Called by `ProxyValidator::validate_trusted_proxy_request`. Uses `HeaderMap`, `TrustedProxyConfig`, `ValidationMode`, `ProxyError`, and IP utilities.

Risks and tests: Strict mode appears to require the client IP itself to be trusted because it checks every IP including the first chain element, which may not match common proxy semantics. Duplicate warning only reports the first duplicate. Unit tests cover hop-by-hop success and chain-too-long error.
