# sources/user-network-fs/gcsfuse/cmd/config_validation_test.go

## Purpose
`config_validation_test.go` validates end-to-end command config loading from CLI flags and YAML files. It checks that generated defaults, config-file unmarshalling, path resolution, validation, rationalization, and selected default values match expected `cfg.Config` structures.

## Important APIs And Test Structure
Helper `getConfigObject` constructs `newRootCmd` with a fake mount function, sets args, runs command execution, and returns captured config. `getConfigObjectWithConfigFile` wraps it for `--config-file`. `defaultFileCacheConfig` builds expected runtime defaults including CPU-based max parallel downloads. Tests cover missing/invalid/empty config files, CLI validation, write/read defaults and overrides, invalid config testdata, file cache, GCS auth, GCS connection, filesystem, list, HNS, metadata cache, GCS retries, metrics interval validation, metrics defaults/invalid cases, and machine type.

## Control Flow And State
Each test executes Cobra command setup without mounting. Config files are read from `cmd/testdata`, unmarshalled with YAML tags and `ErrorUnused`, validated by `cfg.ValidateConfig`, optimized/rationalized, and then captured. The only external state dependency is user home directory resolution for path fields and runtime CPU count for file-cache parallel download defaults.

## Dependencies And Integration
This suite exercises `cmd/root.go`, `cfg/params.yaml`, custom decode hooks, `cfg/validate.go`, `cfg/rationalize.go`, testdata YAML files, and Viper/Cobra binding. It is the main guard that the declarative parameter registry maps correctly into the `cfg.Config` shape and that defaults match user-visible documentation.

## Risks And Test Signals
The tests provide strong regression signal for config compatibility, especially rejected unknown YAML fields, invalid typed values, and defaults per config family. Risks include host-dependent expectations for home directory and CPU count, though helpers account for those. Because the fake command stops before `Mount`, these tests do not validate storage/FUSE side effects; they validate the mount-ready config object.
