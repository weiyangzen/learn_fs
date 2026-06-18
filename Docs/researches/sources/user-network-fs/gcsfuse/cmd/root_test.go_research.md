<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/root_test.go -->
# Research: sources/user-network-fs/gcsfuse/cmd/root_test.go

Purpose: comprehensive unit coverage for the Cobra/Viper root command path. It verifies argument arity, POSIX-style flag normalization, bucket/mount-point extraction, config-file unmarshalling, validation, optimization/rationalization precedence, and logging metadata capture before the real mount function is called.

Important APIs/types/functions: `createTempConfigFile`, `newRootCmd`, `convertToPosixArgs`, `getCliFlags`, `getConfigFileFlags`, and the injected `mountFn` callback are the tested surfaces. The cases cover `cfg.Config` subtrees for write/read/file-cache/auth/connection/filesystem/list/metrics/trace/metadata-cache/retries/profiler/dummy-io/workload-insight plus global feature flags such as HNS, Google auth, atomic rename, new reader, standard symlinks, and unsupported path support.

Control flow and integration: each test builds a fresh command, sets arguments, executes `PersistentPreRunE`, and captures `mountInfo.config` from the fake mount callback. Config-file cases exercise Viper YAML loading, `cfg.DecodeHook`, strict `mapstructure` unused-field rejection, `cfg.ValidateConfig`, `ApplyOptimizations`, and `cfg.Rationalize`; CLI cases assert that explicit flags override config defaults and optimization rules.

State and persistence: tests create only temporary config files and process-local env overrides such as `GCSFUSE_IN_BACKGROUND_MODE`. No mount, GCS, or filesystem state is persisted, but the tests assert the derived `mountInfo` fields that later drive real mounting and config logging.

Dependencies: Go testing, testify assertions, Cobra/pflag argument parsing, Viper config state, `cfg` defaults/validators/decode hooks, path resolution, runtime CPU count for defaults, and platform home/current directories.

Risks: this file is a high-signal compatibility net; flag rename, default drift, new schema fields, optimization-rule changes, and validation-message changes can break many cases. Tests that rely on runtime CPU count or home/current directories should stay value-normalized. Because it focuses on parsing, it does not prove the mounted filesystem honors every parsed value.

Test signals: run `go test ./cmd -run TestArgsParsing`, `go test ./cmd -run TestMountInfoPopulation`, and targeted datatype/config validation tests when changing `cfg` schema, default values, rationalization, or root command wiring.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/root_test.go -->
