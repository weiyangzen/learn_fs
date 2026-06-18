<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/proxy.rs -->
# sources/object-store/rustfs/crates/config/src/constants/proxy.rs

## Purpose
Defines trusted reverse-proxy middleware configuration constants.

## Important APIs, types, and functions
Exports enable/implementation/validation mode/RFC7239/max-hop/chain-continuity/logging keys, default trusted private networks and extra IP/network lists, cache capacity/TTL/cleanup settings, metrics/log/tracing settings, and optional cloud metadata or Cloudflare IP integration keys.

## Control flow
No local logic. Proxy middleware and config loaders use these constants to parse headers and decide whether source addresses and forwarded chains are trusted.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with HTTP request identity extraction, `Forwarded`/`X-Forwarded-*` parsing, metrics, logging, tracing, cloud metadata discovery, and network CIDR parsing.

## Risks and edge cases
Trusted proxy is enabled by default and trusts common private networks; this is convenient behind internal load balancers but dangerous if exposed through untrusted private hops. Cloud metadata discovery is off by default because it can block or leak environment assumptions. Cache TTL affects reaction time to config changes.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Proxy tests should cover hop-by-hop validation, RFC7239 parsing, private-network trust boundaries, cache eviction/TTL, and failed-validation logging.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/proxy.rs -->
