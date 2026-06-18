<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/mount_info_population/cli_override_config.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/mount_info_population/cli_override_config.yaml

Purpose: mount-info CLI override fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `app-name`, `file-system`, `gid`, `logging`, `severity`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It supplies config-file app name, gid, and log severity while tests pass CLI overrides for selected fields. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: mountInfo should record both config-file flags and effective CLI-overridden config.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/mount_info_population/cli_override_config.yaml -->
