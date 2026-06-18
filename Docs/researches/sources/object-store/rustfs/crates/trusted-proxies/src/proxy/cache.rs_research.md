# sources/object-store/rustfs/crates/trusted-proxies/src/proxy/cache.rs

Purpose: Moka-backed cache for direct-peer trusted proxy decisions.

Important APIs/state: `IpValidationCache` stores `Cache<IpAddr, bool>`, capacity, enabled flag, and optional `ProxyMetrics`. Public methods: `new`, `is_trusted`, `clear`, `run_maintenance`, `stats`, and `is_enabled`. `CacheStats` reports size/capacity.

Control flow: Disabled cache executes the validator closure directly. Enabled cache checks Moka for an IP, records hits/misses, invokes the validator on miss, and caches only positive trust decisions to avoid accumulating untrusted client IPs. Maintenance runs pending tasks and updates metrics.

Dependencies and integration: Used by `ProxyValidator` for direct peer trust checks. Metrics methods are optional and no-op when disabled.

Risks and tests: Positive-only caching means repeated untrusted peers always re-run CIDR matching, which is intentional but can cost CPU under hostile traffic. Cache size metric is approximate until pending tasks run. Unit validator tests check trusted decisions populate cache while untrusted/missing/unspecified peers do not.
