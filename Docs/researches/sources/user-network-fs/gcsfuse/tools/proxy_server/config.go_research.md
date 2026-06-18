# sources/user-network-fs/gcsfuse/tools/proxy_server/config.go

Purpose: configuration schema and loader for the HTTP/gRPC proxy server used to inject retry behavior and validate headers.

Important APIs/types/functions: `RetryConfig`, `HeaderValidation`, `Config`, `printConfig`, and `parseConfigFile`.

Control flow: Viper reads the YAML config file and unmarshals into `Config`; `printConfig` logs target, retry configs, and header validation entries.

State/persistence behavior: reads configuration from disk; no writes. Runtime state is passed to `OperationManager` and proxy startup.

Dependencies/integration: used by `main.go`, operation manager, and gRPC metadata validation.

Risks/test signals: unknown YAML keys are ignored, so "invalid" config content can parse successfully into zero-valued fields. Tests explicitly reflect this permissive behavior.
