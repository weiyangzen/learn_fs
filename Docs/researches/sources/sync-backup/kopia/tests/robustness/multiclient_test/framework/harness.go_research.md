<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/harness.go -->
# sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/harness.go

This file assembles the multiclient robustness test harness. `TestHarness` owns repository paths, a temp base directory, multiclient FIO writer, multiclient Kopia snapshotter/server, lightweight metadata persister, and `engine.Engine`. `RepoPathPrefix` controls where shared test repositories live.

Initialization is a linear state machine in `init`: require `repo-path-prefix`, force `ENGINE_MODE=server`, create base dir, require FIO configuration, create snapshotter/server, connect/create the data repo, set cache limits, create metadata persister, connect/create metadata repo, and initialize the engine with repository sync enabled. `Run` and `RunN` run client contexts as parallel subtests and optionally clean up clients. `Cleanup` shuts down the engine, persister, server process, clients, file writers, and temp directory. `GetDirsToLog` collects repo/cache/data paths for storage reporting.

State is both process-local and persisted in shared Kopia repositories. Dependencies include `content.CachingOptions`, FIO/Kopia env vars, `snapmeta`, and `kopiarunner`. Risks include `os.Exit` in setup making failures abrupt, server SIGTERM cleanup races, tiny metadata cache values in bytes, and incomplete cache path collection if `cache info` fails. Signals are all multiclient tests and storage stats logging.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/harness.go -->
