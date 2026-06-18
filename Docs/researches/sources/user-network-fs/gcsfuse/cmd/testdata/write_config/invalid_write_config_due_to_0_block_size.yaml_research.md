<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/write_config/invalid_write_config_due_to_0_block_size.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/write_config/invalid_write_config_due_to_0_block_size.yaml

Purpose: negative streaming write validation fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `write`, `create-empty-file`, `enable-streaming-writes`, `block-size-mb`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It enables streaming writes with `block-size-mb: 0`, below the valid minimum. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: write config validation should reject the invalid streaming write bound.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/write_config/invalid_write_config_due_to_0_block_size.yaml -->
