<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/robustness_test/main_test.go -->
# sources/sync-backup/kopia/tests/robustness/robustness_test/main_test.go

This file is the single-client robustness test harness and `TestMain`. It builds data and metadata repository paths from `repo-path-prefix`, creates FIO writer, Kopia snapshotter, lightweight persister, engine, and an upgrader, restores a previous snapshot into the data directory, optionally upgrades repository format, runs tests, then cleans up.

Initialization is a linear set of boolean steps with skip behavior for missing FIO or `KOPIA_EXE`. `cleanup` shuts down engine metadata, clears upgrade env state, terminates a server command if present, removes temp directories, and cleans FIO/Kopia resources. Upgrade flow reads repository status JSON, runs `repository upgrade begin`, and logs previous/current content format versions.

State persists in shared repositories and in engine metadata; global `eng` is used by test functions. Dependencies are `snapmeta`, `fiofilewriter`, `kopiarunner`, and OS env flags. Risks include abrupt `os.Exit`, global state across tests, cleanup error masking except final check, and repository upgrade side effects. Signals are the single-client robustness tests and upgrade-specific test.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/robustness_test/main_test.go -->
