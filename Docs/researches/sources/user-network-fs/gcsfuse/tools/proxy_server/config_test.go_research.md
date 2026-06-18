# sources/user-network-fs/gcsfuse/tools/proxy_server/config_test.go

Purpose: tests config parsing behavior for valid, empty, and unknown-key YAML files.

Important APIs/types/functions: `TestParseConfigFile`.

Control flow: creates temp YAML files, writes content, calls `parseConfigFile`, and asserts target host and retry config fields for valid input while expecting nil retry configs for empty or unknown-key input.

State/persistence behavior: creates and removes temp files.

Dependencies/integration: depends on `testify/assert`.

Risks/test signals: the invalid-config case asserts no error, documenting that schema validation is not enforced by the loader.
