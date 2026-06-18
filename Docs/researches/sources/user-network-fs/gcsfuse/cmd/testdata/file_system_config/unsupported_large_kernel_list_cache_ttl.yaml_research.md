<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_system_config/unsupported_large_kernel_list_cache_ttl.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/file_system_config/unsupported_large_kernel_list_cache_ttl.yaml

Purpose: oversized kernel list-cache TTL fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `file-system`, `kernel-list-cache-ttl-secs`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `kernel-list-cache-ttl-secs` above the supported int64-duration limit. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: validation should reject the TTL as too high.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_system_config/unsupported_large_kernel_list_cache_ttl.yaml -->
