# sources/user-network-fs/gcsfuse/cmd/config_rationalization_test.go

## Purpose
`config_rationalization_test.go` verifies rationalization behavior through the real Cobra/Viper command path rather than by directly constructing cfg objects. It confirms that CLI flags, generated defaults, validation, optimization application, and `cfg.Rationalize` combine into expected final mount config values.

## Important APIs And Test Structure
The tests reuse `getConfigObject` from command config tests, which builds `newRootCmd` with a fake mount function and captures `mountInfo.config`. `TestRationalizeMetadataCache` covers new TTL flags, deprecated stat/type TTL flags, new stat-cache size, deprecated stat-cache capacity, no relevant flags, mixed old/new flags, and `-1` unlimited sentinels. `TestRationalizeCloudMetricsExportIntervalSecs` covers migration from deprecated `--stackdriver-export-interval` to `CloudMetricsExportIntervalSecs` and direct cloud metrics interval input.

## Control Flow And State
Each test invokes the command with synthetic args ending in a mount argument so Cobra executes `PersistentPreRunE` and the fake mount handler. The captured config is already unmarshalled, validated, optimized, rationalized, and populated with generated defaults. No mounts occur and no persistent state is written.

## Dependencies And Integration
This file integrates the command package with `cfg.Rationalize`, `cfg.BuildFlagSet`, `cfg.BindFlags`, generated defaults from `params.yaml`, and Viper explicit-set detection. It complements `cfg/rationalize_test.go` by proving the same rules survive CLI parsing and default installation.

## Risks And Test Signals
The suite is narrow but high value for backward compatibility around deprecated metadata-cache flags and metrics interval migration. It does not cover config-file rationalization or optimization profiles; those are covered elsewhere. A risk is that `getConfigObject` uses a single fake positional argument, so it validates config setup rather than mount argument permutations.
