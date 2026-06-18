# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/dentry_cache/setup_test.go

Purpose: process-wide setup for dentry-cache integration tests. It configures fallback flag sets for stat, delete, and notifier suites and establishes the common storage client, mount function, mount dir, and root dir.
Important APIs/types/functions: constants `testDirName`, `initialContentSize`, `updatedContentSize`; global `testEnv`, `mountFunc`, `mountDir`, `rootDir`; `env`; helper `mountGCSFuseAndSetupTestDir`; and `TestMain`.
Control flow: `TestMain` parses flags, reads config, populates fallback `DentryCache` config with `--implicit-dirs --experimental-enable-dentry-cache` and TTL variants, detects bucket type, creates a storage client, handles mounted-directory mode, and otherwise runs static mounting tests.
State and persistence: setup creates test directories under `testDirForDentryCache` and stores config-derived mount/log state. Unlike some packages, there is no final explicit GCS cleanup in this file beyond per-test directory setup.
Dependencies and integration points: integrates `test_suite`, `setup`, `client`, and `static_mounting`. Test files call `setup.BuildFlagSets` using run names configured here.
Risks and edge cases: fallback run names must match exported test functions. TTL differences are critical: stat tests need short expiry, delete/notifier tests need long expiry to prove invalidation rather than natural timeout.
Test signals: successful setup yields separate flag-driven suite runs across compatible bucket types with dentry cache enabled.
