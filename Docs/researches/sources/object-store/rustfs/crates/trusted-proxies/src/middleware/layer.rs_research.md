# sources/object-store/rustfs/crates/trusted-proxies/src/middleware/layer.rs

Purpose: Legacy Tower `Layer` implementation that wraps services with the full proxy validator.

Important APIs/state: `TrustedProxyLayer` holds `Arc<ProxyValidator>` and an `enabled` flag. Constructors: `new`, `with_cache_config`, `enabled`, `disabled`, and `is_enabled`. Implements `tower::Layer`.

Control flow: `with_cache_config` builds `ProxyValidator` with config/cache/metrics and starts cache maintenance if enabled. `disabled` constructs a lenient empty config with no metrics. `layer` clones the validator into `LegacyTrustedProxyMiddleware`.

Dependencies and integration: Uses `ProxyValidator`, `TrustedProxyConfig`, `CacheConfig`, `ProxyMetrics`, and Tower. `global.rs` and simplified legacy wrapper use this layer.

Risks and tests: Spawning maintenance only when enabled is correct, but constructor assumes a Tokio runtime is available; validator handles missing runtime by logging. Integration proxy tests exercise this layer in Axum routing.
