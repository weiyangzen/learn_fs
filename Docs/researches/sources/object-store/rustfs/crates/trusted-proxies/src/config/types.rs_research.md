# sources/object-store/rustfs/crates/trusted-proxies/src/config/types.rs

Purpose: Defines trusted proxy configuration data structures and validation modes.

Important APIs/types: `ValidationMode` (`Lenient`, `Strict`, default `HopByHop`) with `FromStr` and `as_str`; `TrustedProxy` (`Single`, `Cidr`) with `contains` and `Display`; `TrustedProxyConfig` with trust/private-network checks and summaries; `CacheConfig`; `MonitoringConfig`; `CloudConfig`; and `AppConfig`.

Control flow: Runtime behavior is mostly simple predicate/composition logic. `TrustedProxyConfig::is_trusted` checks any configured entry against a socket IP. `CloudConfig`/`CacheConfig` convert second counts into `Duration`. Defaults come partly from `rustfs_config` and partly from hard-coded cache defaults.

State and dependencies: Plain cloneable structs with no persistence. Depends on `serde`, `ipnetwork`, `IpAddr`, `SocketAddr`, and `rustfs_config`.

Integration points: Used by loader, validator, middleware layers, global init, cache, and tests. `ValidationMode` drives chain analyzer behavior.

Risks and tests: `TrustedProxyConfig` is mutable only by replacement, which is simple but means hot reload is absent. `ValidationMode::FromStr` accepts `hopbyhop` and `hop_by_hop` but not hyphenated variants. Unit tests cover mode/config basics, trust matching, private network matching, and default proxy constants.
