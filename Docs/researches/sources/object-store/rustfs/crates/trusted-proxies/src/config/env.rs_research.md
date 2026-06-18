# sources/object-store/rustfs/crates/trusted-proxies/src/config/env.rs

Purpose: Small environment helper module for trusted proxy configuration.

Important APIs: `parse_ip_list_from_env`, `parse_string_list_from_env`, `is_env_set`, and `get_all_proxy_env_vars`.

Control flow: `parse_ip_list_from_env` reads an env var or default, splits comma-separated entries, trims empties, parses each entry as `IpNetwork`, logs parse failures, and continues. `parse_string_list_from_env` performs tolerant comma splitting for raw string values such as individual IPs. `get_all_proxy_env_vars` enumerates current proxy-related env values from constants in `rustfs_config`.

State and dependencies: No persistent state. Depends on `std::env`, `ipnetwork`, `rustfs_config` env-name constants, `ConfigError`, and tracing warnings.

Integration points: Used by `ConfigLoader::load_proxy_config` to build CIDR and string lists. Tests in `config_tests.rs` exercise loader defaults/env variables, indirectly checking these helpers.

Risks: `parse_ip_list_from_env` returns `Ok` even when some entries fail, which favors availability but can silently ignore intended trust ranges. `ConfigError` is imported but only used as a return type; invalid entries are logged rather than propagated.
