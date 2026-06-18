# sources/object-store/rustfs/crates/trusted-proxies/src/global.rs

Purpose: Legacy global singleton entrypoints for initializing and accessing the full trusted proxy system.

Important APIs/state: `init`, `layer`, `config`, `metrics`, and `is_enabled`. State is stored in `OnceLock<Arc<AppConfig>>`, `OnceLock<Option<ProxyMetrics>>`, `OnceLock<LegacyTrustedProxyLayer>`, and `OnceLock<bool>`.

Control flow: `init` reads enabled state, exits early when disabled, loads config, initializes metrics if configured, builds a legacy layer with cache config and maintenance task, logs lifecycle/config summary, and leaves singletons initialized forever. Accessors panic if called before successful initialization.

Dependencies and integration: Uses `ConfigLoader`, `LegacyTrustedProxyLayer`, `ProxyMetrics`, defaults/env keys from `rustfs_config`, and `rustfs_utils`. The simplified default implementation can select this legacy path through `simple.rs`.

Risks and tests: `OnceLock` prevents runtime reconfiguration and makes env-dependent tests sensitive to initialization order. If disabled, `CONFIG` and `PROXY_LAYER` remain unset, so calling `legacy_layer` after disabled init panics. No direct requested tests cover these global accessors.
