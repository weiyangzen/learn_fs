# sources/object-store/rustfs/crates/config/src/constants/app.rs

## Purpose
Central application/server/observability constants for RustFS defaults, environment variable names, ports, TLS filenames, docs/license URLs, KMS settings, buffer profile, and binary size units.

## Important APIs, types, and functions
Exports application identity (`APP_NAME`, `VERSION`, `SERVICE_VERSION`), observability defaults, console/server defaults, TLS/cert filenames, URL prefixes, docs/GitHub/license URLs, server env vars, unsupported filesystem policy constants, KMS env/defaults, buffer profile env/default, region/license env vars, logging rotation defaults, `KI_B`, and `MI_B`. `const_str::concat!` builds default addresses and log filename constants.

## Control flow
No runtime logic beyond compile-time constant concatenation. Consumers read constants during config parsing, startup, and observability initialization.

## State and persistence behavior
All values are compile-time constants. They represent defaults and env names rather than mutable runtime state.

## Dependencies and integration points
Uses `const_str::concat`. Integrated by server startup, console setup, TLS loading, disk checks, unsupported filesystem policy, KMS configuration, observability logging/tracing/metrics/profiling, region/license handling, and adaptive buffer profile selection.

## Risks and edge cases
Hard-coded `VERSION`/`SERVICE_VERSION` can drift from package version unless release tooling updates them. `DEFAULT_ADDRESS` and `DEFAULT_CONSOLE_ADDRESS` bind by colon-only host notation, so platform parsing assumptions matter. The MinIO CI compatibility alias can unintentionally bypass disk checks if set in inherited environments.

## Test signals
Unit tests validate basic identity, logging defaults, environment names, TLS filename shape, port separation, address formatting, const-str concatenation, non-empty strings, finite numeric constants, and version/address consistency.
