<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/fio_test.go -->
# sources/sync-backup/kopia/tests/tools/fio/fio_test.go

This file tests FIO runner execution and config translation. It creates runners, runs direct args and config-based jobs, checks global config override behavior, and includes Docker-runner coverage when configured.

Control flow depends heavily on `TestMain` gating via FIO env vars. Tests verify that FIO writes produce expected files and that option overrides produce expected command behavior.

Risks covered include bad executable/image setup, config-to-args translation errors, and Docker volume mapping. Residual risks include platform-specific FIO engines and large robustness workload behavior. These tests are important prerequisites for robustness file writing.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/fio_test.go -->
