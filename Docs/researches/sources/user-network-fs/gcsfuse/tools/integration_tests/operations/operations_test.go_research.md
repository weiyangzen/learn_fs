# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/operations_test.go

Purpose: Provides package-level configuration, constants, shared clients, and `TestMain` orchestration for the operations integration tests.

Important APIs/types/functions: Numerous constants define fixture names and expected object counts for copy/list/delete/create tests. `overrideFilePathsInFlagSet` rewrites `/gcsfuse-tmp` to the actual GCE temp root. `RunTestOnTPCEndPoint` synthesizes a TPC-specific config. `TestMain` handles normal and TPC execution, config fallback, bucket environment setup, storage client creation, mount runs, and auth-variant testing.

Control flow: after parsing flags and config, the package either runs TPC-specific static tests or builds/uses operations config. It initializes GCS test environment and storage client, runs mounted-directory mode if requested, rewrites temp paths for GCE, builds compatible flag sets, then runs static, only-dir, persistent, dynamic, and credential/auth permutations in sequence.

State/persistence: Global `storageClient` and `ctx` are shared by tests. Mount mode and test directory setup are controlled by common setup state. Tests persist objects under `dirForOperationsTest` and mode-specific only-dir prefixes until cleanup by framework helpers.

Dependencies/integration: Integrates with Cloud Storage, static/dynamic/only-dir/persistent mounting packages, credential test runner, and test-suite config structures.

Risks/test signals: Repeated `m.Run()` invocations reuse the same package process and global state, so individual tests must be mount-mode agnostic. The fallback config includes cache, JSON read, gRPC, atomic rename, implicit-dirs, metadata prefetch, and streaming-write variants, making failures useful for regression localization.
