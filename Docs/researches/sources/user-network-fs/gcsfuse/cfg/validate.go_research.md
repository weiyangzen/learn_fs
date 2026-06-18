# sources/user-network-fs/gcsfuse/cfg/validate.go

## Purpose
`validate.go` enforces semantic constraints on a parsed `cfg.Config` before optimization and rationalization make it mount-ready. It rejects malformed URLs, unsupported enum strings, invalid cache/retry/read/write bounds, bad regexes, invalid metrics/tracing settings, incompatible feature combinations, and unsupported optimization profiles.

## Important APIs And Functions
The public API is `ValidateConfig(v *viper.Viper, config *Config) error`. It delegates to focused helpers: log rotation validation; URL validation; file cache bounds and regex compilation; parallel-download prerequisites; metadata prefetch mode validation; sequential read size bounds; TTL bounds; metadata cache limits and deprecated capacity checks; streaming write and buffered read resource bounds; read-stall retry checks; chunk retry/transfer timeout checks; retry max attempts/multiplier/sleep checks; metrics validation; trace exporter and sampling validation; MRD pool size validation; and profile validation for `aiml-training`, `aiml-serving`, and `aiml-checkpointing`.

## Control Flow And State
`ValidateConfig` runs validators sequentially and wraps the first error with a config-family prefix. Some retry validators run only if Viper says the corresponding key was explicitly set, preserving compatibility with default zero values that rationalization later interprets as unlimited. Metadata cache validation similarly only validates new TTL and stat-cache-size fields when Viper marks the new key as set, while always checking type-cache size, deprecated capacity, and metadata prefetch sentinels. The function does not mutate or persist config state; it only returns errors.

## Dependencies And Integration
The file depends on `regexp` for include/exclude regex validation, `net/url` through `decodeURL`, `math` for port/int boundaries, `time`, `strings`/`slices`, `internal/util` for MiB limits, and `viper` for explicit-set semantics. `cmd/root.go` calls `ValidateConfig` after Viper unmarshalling and before `ApplyOptimizations` and `Rationalize`. Mount code relies on these checks before using values in storage clients, FUSE mount config, gcsx bucket config, fs server config, metrics exporters, tracing, and read/write schedulers.

## Risks And Test Signals
The primary risk is that validation depends on exact Viper key names, so generated parameter path changes can bypass explicit-only checks. Another risk is intentional permissiveness: negative metrics intervals and negative Prometheus ports are not rejected except for port values above `MaxUint16`, which may be compatibility-driven but can surprise maintainers. `cfg/validate_test.go` provides broad positive and negative coverage for file cache, URLs, metadata cache, read/write, retries, metrics, tracing, log severity, profiles, and MRD. `cmd/config_validation_test.go` verifies the same constraints through real command/config-file paths and testdata YAML.
