<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/setup_test.go

Purpose: Package-level TestMain and environment setup for buffered-read integration tests.

Important APIs, types, and functions: Defines constants `testDirName`, `testFileName`, `blockSizeInBytes`, and `GKETempDir`, globals `mountFunc`, `mountDir`, `rootDir`, and `testEnv`, plus `env` structure. `TestMain` builds default buffered-read configs when config file lacks them.

Control flow: Parses setup flags, reads config or synthesizes three config items for sequential reads, insufficient pool creation, and random fallback. It initializes context/storage client, handles mounted-directory mode, sets up test bucket directory, rewrites GKE-specific log paths for GCE, selects static mounting, runs tests, then cleans up GCS test directory.

State and persistence behavior: Creates Cloud Storage client and test directory, modifies config flag paths, and cleans test bucket directory after suite. Mount state is managed in individual suites.

Dependencies and integration points: Depends on `internal/util` for MiB, integration setup/client/static mounting/test suite utilities, and Cloud Storage.

Risks and test signals: Defaults hard-code trace log paths under `/gcsfuse-tmp`, which must be overridden or available. Shared globals couple all buffered-read test files. Cleanup at package end may leave objects if process exits early.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/setup_test.go -->
