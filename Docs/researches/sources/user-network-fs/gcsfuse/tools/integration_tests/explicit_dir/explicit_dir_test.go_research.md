# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/explicit_dir/explicit_dir_test.go

Purpose: process-wide setup for tests where implicit directories are disabled and only explicit directory objects should be surfaced.
Important APIs/types/functions: constant `DirForExplicitDirTests`; `env` with storage client and context; global `testEnv`; `TestMain`.
Control flow: `TestMain` parses flags, reads config, populates fallback `ExplicitDir` config with `--implicit-dirs=false` and gRPC variant for compatible flat buckets, creates storage client, builds flag sets, and delegates execution to `implicit_and_explicit_dir_setup.RunTestsForExplicitAndImplicitDir`.
State and persistence: test data is created under `dirForExplicitDirTests`; setup itself stores context/client only. Mount lifecycle is delegated to the shared implicit/explicit directory setup helper.
Dependencies and integration points: integrates `test_suite`, `setup`, `client`, and `implicit_and_explicit_dir_setup`. Test files rely on `testEnv` and the shared directory constants.
Risks and edge cases: compatibility marks HNS/zonal false in fallback config, so coverage depends on external config for other bucket types. The package name uses `_test`, so it exercises public utility APIs only.
Test signals: successful setup yields flag-specific runs where explicit-only listing/stat behavior can be asserted.
