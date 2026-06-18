<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/main_test.go -->
# sources/sync-backup/kopia/tests/tools/fio/main_test.go

This file controls FIO test execution. `TestMain` checks `FIO_EXE` and `FIO_DOCKER_IMAGE` environment variables and exits/skips behavior appropriately for tests that require external FIO capability.

The integration purpose is to avoid failing normal test runs when FIO is unavailable, while enabling real I/O tests in configured environments.

State is only process environment. Risks include accidentally skipping coverage in CI if env is absent, or running destructive/heavy I/O tests when env points to an unexpected executable/image. Signals are all tests in the `fio` package.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/main_test.go -->
