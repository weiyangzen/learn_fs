<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/credentials_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/auth/credentials_test.go

Purpose: unit tests for credential discovery option construction and error wrapping.

Important APIs/types/functions: `MockDetectCredentials`, `Test_getCredentials_Success`, and `Test_getCredentials_Error`.

Control flow: a testify mock expects exact `credentials.DetectOptions` for key-file and ADC-style empty key-file cases, then returns either credentials or a simulated error.

State and persistence: no external credentials are read; tests use mocks only.

Dependencies: testify mock/assertions and cloud auth types.

Risks: exact struct matching can break if detect options gain default fields. The tests do not exercise real ADC metadata-server behavior.

Test signals: `go test ./internal/auth -run getCredentials`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/credentials_test.go -->
