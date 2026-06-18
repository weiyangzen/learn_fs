# sources/user-network-fs/gcsfuse/cfg/validate_test.go

## Purpose
`validate_test.go` is the package-level test suite for config semantic validation and custom log severity behavior. It constructs in-memory config values to verify that `ValidateConfig` and helper validators accept supported combinations and reject unsafe or unsupported values.

## Important APIs And Test Structure
The file defines helper builders such as `validLogRotateConfig`, `validFileCacheConfig`, regex variants, and `validConfig`. Tests cover successful configs, broad error scenarios, TTL bounds, streaming write error/success cases, buffered read error/success cases, MRD pool size, metrics, tracing/monitoring, log severity ranks, optimization profile validation, max retry attempts, retry multiplier, and max retry sleep. Assertions use `testify/assert`, and some tests use `t.Parallel()`.

## Control Flow And State
Each test table constructs a `Config`, optionally a Viper instance, invokes a validator, and asserts error or no error. The suite includes direct helper tests to isolate boundary behavior from the full `ValidateConfig` chain. It has no persistent state and only uses process information indirectly for architecture-sensitive retry-attempt overflow coverage, skipping the MaxInt overflow test on 64-bit systems.

## Dependencies And Integration
These tests document the contracts that command-level parsing must satisfy before mount setup. The cases map directly to `params.yaml` defaults and mount consumers: file cache and parallel downloads, metadata cache TTL/capacity, write/read block accounting, read-stall retry knobs, chunk retry timeouts, metrics exporter workers/buffer/port, trace exporters, log severity ranking, and profile names.

## Risks And Test Signals
The suite is strong for helper-level boundary checks but does not exercise Viper unmarshalling or generated defaults in most cases. It also encodes current permissive behavior for negative metrics intervals and negative Prometheus ports, so future tightening would require explicit compatibility decisions. Together with command-level config-file tests, it gives high signal that invalid runtime values are blocked before storage/FUSE setup.
