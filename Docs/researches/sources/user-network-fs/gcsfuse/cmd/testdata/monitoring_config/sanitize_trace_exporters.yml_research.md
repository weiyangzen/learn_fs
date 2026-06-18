<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/monitoring_config/sanitize_trace_exporters.yml -->
# Research: sources/user-network-fs/gcsfuse/cmd/testdata/monitoring_config/sanitize_trace_exporters.yml

Purpose: trace exporter normalization fixture for gcsfuse command/config tests.

Important data and APIs: YAML fixture data with `trace`, `exporters`, `sampling-ratio`, `project-id`. It is not executable code; its public contract is the exact schema and scalar values consumed through Viper, mapstructure YAML tags, and `cfg.DecodeHook`/`cfg.ValidateConfig`.

Control flow and integration: It uses mixed-case comma-separated trace exporters and a sampling ratio/project to verify sanitizer behavior. Tests load it through `--config-file` or helper Viper instances, then execute `newRootCmd` pre-run logic or config validation before any real mount occurs.

State and persistence: static repository test data only. It creates no runtime state beyond parsed config maps in tests.

Dependencies: depends on `cfg.Config` field names, YAML/JSON parser behavior, duration/octal/log severity/protocol decode hooks, and validation rules in `cfg/validate.go`.

Risks: changing field names, defaults, or accepted sentinel values can make this fixture stale. Invalid fixtures are valuable because relaxing strict unmarshalling would hide typos in user config files.

Test signals: trace parsing should normalize exporters to gcpexporter/stdout and keep sampling/project.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/cmd/testdata/monitoring_config/sanitize_trace_exporters.yml -->
