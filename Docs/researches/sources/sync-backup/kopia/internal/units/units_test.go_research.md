<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/units/units_test.go -->
# sources/sync-backup/kopia/internal/units/units_test.go

- Purpose: Tests base-10/base-2 byte formatting and environment-controlled selection.
- Important APIs/types/functions: `base10Cases`, `base2Cases`, `TestBytesStringBase10`, `TestBytesStringBase2`, `TestBytesString_base2EnvFalse`, `TestBytesString_base2EnvTrue`.
- Control flow: Table tests iterate numeric boundaries from bytes through exabytes and assert exact formatted strings; env tests use `t.Setenv`.
- State and persistence: Environment variable is scoped by test helper cleanup.
- Dependencies and integration points: Uses `testify/require`.
- Risks and edge cases: Does not cover `BytesPerSecondsString` or `Count` directly, but shared scaling code is covered.
- Test signals: Direct coverage for core unit formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/units/units_test.go -->
