<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/setup_test.go

Purpose: TestMain and shared helpers for benchmarking integration tests.

Important APIs, types, and functions: Defines package globals `testEnv`, `mountFunc`, `mountDir`, and `rootDir`; `env` stores storage client, context, test directory, config, and bucket type. Helpers include `mountGCSFuseAndSetupTestDir` and `createFiles`. `TestMain` parses flags/config and initializes environment.

Control flow: `TestMain` reads config; if absent, it synthesizes benchmarking configs for stat, rename, and delete with flat/grpc variants. It creates a storage client, handles mounted-directory mode, sets up test bucket mount directories, selects static mounting, runs benchmarks, then cleans the GCS test directory.

State and persistence behavior: Creates a test directory in the bucket, mounts/unmounts gcsfuse via benchmark tests, and deletes GCS test data on completion. Global test environment is shared by benchmark files.

Dependencies and integration points: Depends on Cloud Storage client, integration setup/client/operations utilities, static mounting, and test suite config schema.

Risks and test signals: Benchmark files rely on shared global state initialized here. If cleanup fails, benchmark objects may remain. Fallback default config makes the package runnable without YAML but may drift from release config.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/setup_test.go -->
