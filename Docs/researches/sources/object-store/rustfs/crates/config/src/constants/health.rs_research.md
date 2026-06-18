<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/health.rs -->
# sources/object-store/rustfs/crates/config/src/constants/health.rs

## Purpose
Defines health endpoint and readiness probe configuration names and defaults.

## Important APIs, types, and functions
`ENV_HEALTH_ENDPOINT_ENABLE` defaults public health/ready routes on. `ENV_HEALTH_READINESS_CACHE_TTL_MS` defaults readiness cache TTL to 1000 ms. Other flags control minimal response payloads, busy protection by active request count, and optional KMS readiness participation.

## Control flow
No local control flow; endpoint registration and readiness evaluation happen in HTTP/server layers that consume these constants.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with HTTP route setup, storage readiness checks, request accounting, and optional KMS manager state.

## Risks and edge cases
Health endpoints default to enabled, which is useful for orchestration but exposes status unless deployment routing controls it. Readiness cache can hide rapid state changes for up to the configured TTL. Busy/KMS checks are opt-in and can change compatibility semantics for probes.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Health endpoint tests should assert route registration, 404 when disabled, readiness-cache TTL behavior, minimal payload mode, busy 429 behavior, and KMS gating.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/health.rs -->
