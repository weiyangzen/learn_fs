# sources/object-store/rustfs/crates/trusted-proxies/tests/unit/config_tests.rs

Purpose: Unit tests for trusted proxy config loading and config data structures.

Important APIs tested: `ConfigLoader::from_env_or_default`, `ConfigLoader::from_env`, `TrustedProxyConfig::new`, `TrustedProxy::contains`, `TrustedProxyConfig::is_trusted`, `is_private_network`, `ValidationMode`, and default proxy constants.

Control flow: Serial env tests clear/set relevant variables using `temp_env`, verify defaults and env overrides, then independent tests validate single-IP/CIDR matching and private-network matching.

State and dependencies: Uses serial execution for env-mutating tests. Depends on `rustfs_config` constants and public trusted-proxies exports.

Integration points: Covers config path consumed by global legacy initialization and validator construction.

Risks and coverage gaps: Does not assert invalid env values, fallback behavior when validation mode is malformed, cloud/cache/monitoring env fields, or individual IP list parsing.
