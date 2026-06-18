## sources/user-network-fs/gcsfuse/.gemini/skills/integration-tests/templates/setup_test.go

Purpose: Template `TestMain` environment bootstrap for gcsfuse integration-test packages.

Important APIs/types/functions: constants `testDirName` and `onlyDirMounted`; `env` struct holding mount function, mount/root dirs, GCS storage/control clients, context, config, bucket type, and current test dir; global `testEnv`; `TestMain` orchestrates configuration, clients, mounting modes, cleanup, and process exit.

Control flow: parse common flags, read integration config, require `DummyTestPackage` config, detect bucket type/environment, create storage/control clients with deferred close, short-circuit if `GKEMountedDirectory` is configured, otherwise prepare local test dirs, run static mounting tests, if successful run dynamic mounting tests, if successful run only-dir mounting tests, then cleanup test directories in GCS and exit with the final suite code.

State and persistence: creates local/mount directories, uses real GCS bucket paths, and removes package test prefixes at the end. It stores clients and config in global `testEnv` for suite files.

Dependencies and integration points: imports Cloud Storage data/control clients and gcsfuse integration utilities for setup, client creation, static/dynamic/only-dir mounting, and test configuration.

Risks: template package/config names must be updated consistently. Because it may run real bucket operations, incorrect test bucket or only-dir paths can delete unintended test prefixes. `log.Fatalf` stops early if config is absent. Control client setup is included even though comments say many packages can omit it.

Test signals: success is observed through `go test` package execution across static, dynamic, only-dir, and mounted-directory paths, with cleanup and client-close logging.
