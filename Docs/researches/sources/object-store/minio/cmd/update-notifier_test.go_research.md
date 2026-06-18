# sources/object-store/minio/cmd/update-notifier_test.go

Tests `prepareUpdateMessage` formatting for MinIO update notifications. The table covers suppression for empty download URLs and non-positive age, plus duration wording across seconds, minutes, hours, days, weeks, months, and years.

Important dependencies are `testing`, `strings`, `fmt`, `time`, and `internal/color`. The test asserts colorized substrings for the "older version" line and update URL line rather than exact whole output.

There is no persistence or external integration. The main signal is user-facing message regression coverage; terminal width, ANSI-disabled output, and full layout are not covered.
