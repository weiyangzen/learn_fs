# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/grpc_header_validation/grpc_header_validation_test.go

Purpose: verifies that gcsfuse's gRPC client sends DirectPath-related metadata headers through a proxy to the emulator gRPC testbench.
Important APIs/types/functions: `grpcHeaderValidation` suite with proxy port/PID/log/config/flags fields; `SetupTest`, `TearDownTest`, `TestGRPCClientSendsExpectedHeaders`, `TestGRPCHeadersInMultipleOperations`, and `TestGRPCHeaderValidation`.
Control flow: setup starts the gRPC validation proxy, appends `--custom-endpoint` and `--anonymous-access`, then mounts with `--client-protocol=grpc`. Tests either rely on mount-triggered DirectPath calls or perform write/read/stat/list operations and inspect proxy logs.
State and persistence: mounted file operations create test data in the emulator bucket. Validation state is proxy log text, including metadata validation markers and method names.
Dependencies and integration points: integrates emulator util `StartProxyServer`, static mount setup, config `grpc_header_validation.yaml`, and storage-testbench gRPC server from `emulator_tests.sh`.
Risks and edge cases: method count assertions are brittle if gcsfuse adds extra `GetObject`, prefetch, or validation calls. The localhost gRPC endpoint requires anonymous access.
Test signals: logs must include DirectPath metadata patterns, diagnostic value `no_auth`, `Metadata validation passed`, and expected counts for GetObject/BidiWriteObject/ReadObject/ListObjects.
