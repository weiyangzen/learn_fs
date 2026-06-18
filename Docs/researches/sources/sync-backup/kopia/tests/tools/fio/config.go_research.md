<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/config.go -->
# sources/sync-backup/kopia/tests/tools/fio/config.go

This file defines `Config` as a slice of FIO `Job` values and provides `Config.String` for rendering a human-readable fio-style configuration. It joins each job string with blank lines.

The string method is primarily diagnostic; actual runner execution converts configs directly to CLI arguments in `fio.go`. It integrates with debug logging when `Runner.Debug` is enabled.

There is no state. Risks are low, limited to formatting expectations in tests or logs. Unit tests for FIO config/run behavior validate the rendered structure indirectly and directly.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/config.go -->
