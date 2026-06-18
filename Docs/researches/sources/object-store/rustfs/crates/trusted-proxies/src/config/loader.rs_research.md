# sources/object-store/rustfs/crates/trusted-proxies/src/config/loader.rs

Purpose: Loads complete trusted-proxies runtime configuration from environment and defaults.

Important APIs: `ConfigLoader::from_env`, `from_env_or_default`, `default_config`, and `print_summary`; private loaders for proxy, cache, monitoring, cloud, and server address.

Control flow: `from_env` composes `AppConfig` from five loading steps. Proxy loading parses configured CIDR proxies, extra proxies, individual IPs, validation mode, RFC7239 toggle, max hops, continuity checks, and private networks. Cache, monitoring, and cloud loading are direct env/default reads via `rustfs_utils`. Server binding reads `RUSTFS_ADDRESS` and falls back to IPv6 unspecified plus default port if parsing fails. `from_env_or_default` logs success or falls back to `default_config` on any loader error.

State and dependencies: Stateless loader depending on `rustfs_config` constants, `rustfs_utils` env/address helpers, `IpNetwork`, `SocketAddr`, and crate config/error types.

Integration points: `global::init` calls `from_env_or_default`; middleware/layer construction receives the resulting proxy and cache configs. Unit config tests cover defaults, env override of proxies/mode/max hops, `TrustedProxyConfig` behavior, private network checks, and expected default string constants.

Risks: Individual IP parsing silently drops bad values. Any invalid validation mode causes full fallback in `from_env_or_default`, potentially replacing otherwise valid user config. Server address parse failures are silently normalized to default bind address.
