<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_parallel_downloads_per_file.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_parallel_downloads_per_file.yaml

Purpose: negative per-file download fanout fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `file-cache`, `cache-file-for-range-read`, `parallel-downloads-per-file`, `max-parallel-downloads`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It verifies `parallel-downloads-per-file` must be at least 1. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: config validation should reject the per-file parallel download count.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/file_cache_config/invalid_parallel_downloads_per_file.yaml -->
