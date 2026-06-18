# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/emulator_tests.sh

Purpose: orchestration script for all emulator-backed integration tests. It installs/validates Docker, starts storage-testbench HTTP and gRPC endpoints, creates `test-bucket`, and runs `go test` for `./tools/integration_tests/emulator_tests/...`.
Important functions and variables: `log_info`, `log_error`, `wait_for_emulator`, `cleanup`, `TEST_INSTALLED_PACKAGE`, `GCSFUSE_PREBUILT_DIR`, `STORAGE_EMULATOR_HOST`, `STORAGE_EMULATOR_HOST_GRPC`, docker image/name variables, and final `args` passed to Go tests.
Control flow: validates mutually exclusive package/prebuilt modes, skips arm64 and old Go, installs Docker/lsof if needed, pulls/runs storage-testbench with host networking and extended Gunicorn timeout, waits for readiness, creates bucket, starts gRPC on port 8888, then runs tests serially with `-p 1`.
State and persistence: creates a Docker container, `emulator_container.log`, temporary `test.json`, and environment variables. Cleanup stops the container, unsets emulator env vars, prints logs, and removes temp JSON.
Dependencies and integration points: depends on Linux host networking, sudo Docker, curl, Go tooling, storage-testbench image, and optional built gcsfuse path from the parent e2e runner.
Risks and edge cases: host networking and fixed ports can conflict with other local services. Docker installation mutates the host. Serial package execution reduces CPU pressure but can lengthen CI time.
Test signals: readiness curl, successful bucket creation, HTTP 200 from `/start_grpc`, and passing `go test` establish emulator infrastructure health.
