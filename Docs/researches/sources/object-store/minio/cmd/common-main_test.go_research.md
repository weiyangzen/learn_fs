# sources/object-store/minio/cmd/common-main_test.go

## Purpose
`common-main_test.go` verifies the smaller, deterministic helpers in `common-main.go` that parse secret files and environment configuration files.

## Important APIs, Types, And Functions
`Test_readFromSecret` writes temporary secret files and checks that `readFromSecret` trims whitespace/newlines while preserving meaningful content. `Test_minioEnvironFromFile` exercises `minioEnvironFromFile` and indirectly `parsEnvEntry` for `export` syntax, plain syntax, single and double quotes, comments, blank lines, and malformed entries.

## Control Flow
Each test creates a temporary file, writes the test case content, syncs/closes it, calls the target helper, and compares returned values or expected error behavior. The env-file test uses `reflect.DeepEqual` on `[]envKV`.

## State And Persistence Behavior
Only temporary files under `t.TempDir()` are written. The tests do not mutate real process environment variables and do not invoke fatal startup paths.

## Dependencies And Integration Points
The tests depend on `os.CreateTemp`, `errors`, `reflect`, and the `envKV` type from `common-main.go`. They validate inputs used by Docker/Kubernetes secret and `MINIO_CONFIG_ENV_FILE` workflows.

## Risks And Test Signals
The suite is intentionally narrow. It does not cover missing secret files, `/run/secrets` fallback, scanner token-size limits, inline comments, escaped quotes, or `loadEnvVarsFromFiles` mutation behavior. It is a useful regression signal for the supported simple env-file grammar.
