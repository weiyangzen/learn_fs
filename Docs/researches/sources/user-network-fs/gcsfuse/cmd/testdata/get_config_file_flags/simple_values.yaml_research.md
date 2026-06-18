<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/get_config_file_flags/simple_values.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/get_config_file_flags/simple_values.yaml

Purpose: config-file flag extraction scalar fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `key1`, `key2`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It verifies scalar values are returned from the raw config file without injected defaults. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: test should return only key1/key2 from the file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/get_config_file_flags/simple_values.yaml -->
