<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/observability/mod.rs -->
# sources/object-store/rustfs/crates/config/src/observability/mod.rs

## Purpose
Defines observability environment keys and defaults for OTLP endpoints, per-signal export toggles, logging, log cleanup, compression, and environment names.

## Important APIs, types, and functions
Exports endpoint/header/timeout keys for traces, metrics, logs, profiling, stdout/sample/meter/service metadata keys, per-signal export flags, logger level/stdout/file rotation keys, cleanup sizing/compression/retention/dry-run/match-mode keys, and defaults including 2 GiB total log cap, zstd compression, parallel compression, 30-day compressed retention, and production/development/test/staging environment strings.

## Control flow
Module re-exports `metrics` and uses `const_str::concat!` to build compression extensions. Tests assert env-key names and default values.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with tracing/metrics/log/profiling exporters, file log rotation, cleanup workers, compression libraries, and service metadata.

## Risks and edge cases
Logging cleanup can delete or compress operator artifacts if match modes or exclude patterns are wrong. Endpoint header values may contain secrets. Compression defaults add CPU use but reduce disk pressure. Environment names may drive security-sensitive stdout behavior.

## Test signals
Unit tests pin key/default names. Integration tests should cover per-signal enablement, endpoint-specific headers/timeouts, cleanup dry run, retention, compression fallback, and match/exclude behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/observability/mod.rs -->
