<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/multiclient_test.go -->
# sources/sync-backup/kopia/tests/robustness/multiclient_test/multiclient_test.go

This file defines concurrent robustness scenarios against a shared Kopia server. Tests cover many small files, one large file, a broad directory tree, randomized small actions, direct maintenance/GC, and delete-random-snapshot behavior. Each scenario builds FIO options and calls `th.RunN` with client contexts.

Control flow for each client usually restores an existing snapshot into its data directory, performs deletes that tolerate `ErrNoOp`, writes files, snapshots, and restores/compares. `TestRandomizedSmall` loops until `rand-test-duration`, weighting actions through `engine.ActionOpts`. Helper functions mask expected `ErrNoOp` for restore/delete/random actions while asserting hard failures.

State is intentionally shared through the global engine, server repository, metadata repository, and per-client data dirs. Dependencies are `engine.ActionKey`, `fiofilewriter` option fields, `testlogging`, and `timetrack`. Risks include long runtimes, shared global engine concurrency assumptions, randomized non-reproducibility, and maintenance running directly against a repository with active server clients. Signals are the tests themselves.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/multiclient_test.go -->
