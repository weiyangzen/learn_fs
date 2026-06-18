## sources/user-network-fs/gcsfuse/cfg/defaults.go

Purpose: Provides startup-safe default logging configuration before full config parsing.

Important APIs/types/functions: `DefaultLoggingConfig() LoggingConfig` returns severity `INFO`, format `json`, and log rotation defaults of backup count 10, compression enabled, and max file size 512 MiB.

Control flow: constructs and returns a literal `LoggingConfig`.

State and persistence: stateless; no file logging is opened here.

Dependencies and integration points: uses `LoggingConfig` and `LogRotateLoggingConfig` from generated config types. Intended for application startup when parsed config is not yet available.

Risks: defaults should stay aligned with generated flag defaults in `config.go`; drift would cause startup logging to differ from parsed config.

Test signals: no direct test in this subset; can be checked by startup logging behavior and config default tests.
