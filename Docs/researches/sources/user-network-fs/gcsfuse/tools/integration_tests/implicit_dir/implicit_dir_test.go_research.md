# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/implicit_dir/implicit_dir_test.go

Purpose: process-wide setup for tests with `--implicit-dirs` enabled. It defines constants used by deletion/list/local-file tests and drives execution through shared implicit/explicit directory setup.
Important APIs/types/functions: constants for explicit dirs inside implicit dirs, file prefixes/counts, and `DirForImplicitDirTests`; `env`; global `testEnv`; `setupTestDir`; and `TestMain`.
Control flow: setup parses flags, reads config, populates fallback `ImplicitDir` config with HTTP and gRPC variants, creates storage client, builds compatible flag sets, runs tests with `RunTestsForExplicitAndImplicitDir`, saves logs on failure, and cleans up GCS test prefix.
State and persistence: test data lives under `dirForImplicitDirTests` and additional local-file test prefixes. `setupTestDir` creates a mounted subdirectory under the package root test dir.
Dependencies and integration points: integrates setup/test_suite/client helpers and shared implicit/explicit setup utilities. Other files depend on constants and `testEnv`.
Risks and edge cases: cleanup path references `testDirName`, a constant declared in `local_file_test.go` in the same package; this cross-file dependency is legal but non-obvious. gRPC variant excludes zonal buckets.
Test signals: setup success enables implicit directory visibility, deletion, symlink, and local-file behavior to be tested across configured bucket types.
