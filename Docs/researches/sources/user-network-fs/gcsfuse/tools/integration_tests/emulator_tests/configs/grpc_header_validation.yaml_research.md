# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/grpc_header_validation.yaml

Purpose: configures the proxy server as a gRPC metadata validator for DirectPath header behavior against storage-testbench's gRPC endpoint.
Important keys: `proxyType: grpc`, `targetHost: localhost:8888`, and two `headerValidation` rules for `x-goog-request-params` matching `force_direct_connectivity=ENFORCED` and `direct_connectivity_diagnostic`.
Control flow: for matching gRPC calls, the proxy inspects metadata and fails on mismatch. Tests later scan proxy logs for validation success and expected method names.
State and persistence: stores validation rules only. Runtime state is proxy log content and the emulator bucket.
Dependencies and integration points: used by `grpc_header_validation_test.go`, which starts the proxy and mounts gcsfuse with `--client-protocol=grpc` plus localhost custom endpoint.
Risks and edge cases: depends on Go Storage SDK metadata formatting and DirectPath diagnostic keys. Method counts in tests can change if gcsfuse adds prefetch or extra validation calls.
Test signals: proxy logs contain `Metadata validation passed`, request params, diagnostic metadata, and expected `google.storage.v2.Storage` method paths.
