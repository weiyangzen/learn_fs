<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/float4.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/float4.yaml

Purpose: positive fractional float fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `gcs-connection`, `limit-bytes-per-sec`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It sets `limit-bytes-per-sec: 12.5`. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: the relevant root/config tests should parse, validate, or reject this fixture according to its name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/float4.yaml -->
