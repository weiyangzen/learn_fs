# sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/sentry_test.go

Purpose: tests for crash report parsing and fingerprint normalization in the crash receiver Sentry integration.

Important APIs/types/functions: `TestParseReport` loads `_testdata/*.log`, calls `parseCrashReport`, serializes packet JSON, and prints it. `TestCrashReportFingerprint` table-tests panic messages, expected sanitized fingerprint text, and whether LevelDB-specific grouping should collapse to one fingerprint element.

Control flow: parse test iterates all fixture logs and fails on glob/read/parse/JSON errors. Fingerprint test calls `crashReportFingerprint`, checks expected length (`1` for LevelDB-sanitized messages, `2` for default-plus-message fingerprints), and compares sanitized message.

State and persistence behavior: read-only fixture access; test output prints packet JSON but writes no files.

Dependencies/integration: exercises `parseCrashReport`, Sentry packet JSON generation, version parsing, panicparse, source loader behavior, and regex sanitizers.

Risks/test signals: `TestParseReport` has weak assertions beyond parse/JSON success, so packet content regressions may require golden tests to catch. Fingerprint cases are strong regression signals for known LevelDB and runtime panic patterns.
