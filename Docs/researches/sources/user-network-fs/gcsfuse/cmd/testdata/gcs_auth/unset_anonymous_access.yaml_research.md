<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_auth/unset_anonymous_access.yaml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_auth/unset_anonymous_access.yaml

Purpose: GCS auth defaulting fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `write`, `create-empty-file`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It omits `gcs-auth` while setting an unrelated write flag, proving auth defaults remain in effect. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: root config parsing should succeed with default anonymous-access false.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/gcs_auth/unset_anonymous_access.yaml -->
