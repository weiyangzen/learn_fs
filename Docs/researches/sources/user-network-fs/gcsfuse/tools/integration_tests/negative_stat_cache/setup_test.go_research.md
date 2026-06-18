# sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/setup_test.go

Purpose: Provides package-wide setup for negative stat cache tests, including fallback config generation, global clients, mount-mode selection, and cleanup.

Important APIs/types/functions: constants `testDirName` and `onlyDirMounted`; `env` centralizes mount function, mount/root paths, storage clients, context, config, bucket type, and active test directory; `TestMain` orchestrates the full package lifecycle. Fallback config defines disabled, finite, and infinite negative TTL runs via `test_suite.ConfigItem.Run`.

Control flow: `TestMain` parses flags, reads config, synthesizes config if absent, initializes `context.Background`, discovers bucket type via `setup.TestEnvironment`, creates data and control storage clients, handles GKE mounted-directory mode, then runs static, dynamic, and only-dir mount passes sequentially. It stops on first nonzero test code and exits with the final code.

State/persistence: `testEnv` is shared by all package test files. Static and dynamic mount modes reuse root directories differently; only-dir mode sets `setup.OnlyDirMounted` and later removes the only-dir prefix from GCS. Storage clients are closed with deferred callbacks.

Dependencies/integration: Integrates with Google Cloud Storage data/control APIs, `static_mounting`, `dynamic_mounting`, `only_dir_mounting`, and common setup/config helpers.

Risks/test signals: Sequential `m.Run()` calls rely on test packages being written to tolerate repeated runs with different mount state. Cleanup must include both normal and only-dir prefixes or later package passes may observe stale objects. The config compatibility matrix is the key signal that all bucket types are intended for these tests.
