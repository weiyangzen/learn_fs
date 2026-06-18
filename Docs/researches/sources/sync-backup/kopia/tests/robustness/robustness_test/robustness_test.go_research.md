<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/robustness_test/robustness_test.go -->
# sources/sync-backup/kopia/tests/robustness/robustness_test/robustness_test.go

This file defines single-client robustness scenarios. It mirrors the multiclient workloads at lower concurrency: many small files, one large file, directory-tree writes, and randomized small actions.

Each test creates FIO options, executes engine actions, tolerates expected `robustness.ErrNoOp` for deletes/restores where appropriate, and asserts snapshot/restore success. The randomized test builds weighted `engine.ActionOpts` and loops until `randomizedTestDur`.

State and persistence are provided by the global engine from `main_test.go`, which persists logs, stats, and snapshot metadata between runs. Dependencies are `engine`, `fiofilewriter`, `require`, and test logging. Risks include random long-running behavior, hidden option parse fallbacks, and coupling to previous repository contents. Test signals directly validate end-to-end backup/restore consistency under mutations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/robustness_test/robustness_test.go -->
