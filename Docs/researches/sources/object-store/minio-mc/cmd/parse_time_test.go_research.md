# Research: sources/object-store/minio-mc/cmd/parse_time_test.go

## sources/object-store/minio-mc/cmd/parse_time_test.go

Purpose: tests the custom duration parser used by commands with age/time flags such as `--older-than` and `--newer-than`.

Important APIs and data: `parseDurationTests` enumerates valid and invalid strings for `ParseDuration`; `TestParseDuration` checks parser success and exact `Duration` values; `TestParseDurationTime` adds command-style day/hour/minute scenarios and expected error strings.

Control flow: table tests run subtests over simple units, signs, decimals, composite durations, weeks/days, very large values, fractional precision, and overflow cases. Invalid cases require non-nil errors.

State and persistence: test-only, no persistent mutation.

Dependencies and integration: relies on package constants `Nanosecond`, `Microsecond`, `Millisecond`, `Second`, `Minute`, `Hour`, `Day`, `Week`, and type `Duration` defined elsewhere. These tests indirectly protect filtering flags used by mirror, move, and replication resync.

Risks and test signals: tests include Unicode microsecond symbols, so source encoding matters. Error matching in `TestParseDurationTime` only checks mismatching non-nil errors; if an expected error case returns nil with expected zero value, it would not fail for the error string.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/parse_time_test.go -->
