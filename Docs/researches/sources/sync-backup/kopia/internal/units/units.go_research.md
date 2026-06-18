<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/units/units.go -->
# sources/sync-backup/kopia/internal/units/units.go

- Purpose: Formats byte sizes, rates, and counts into compact human-readable strings.
- Important APIs/types/functions: `BytesStringBase10`, `BytesStringBase2`, `BytesString`, `BytesPerSecondsString`, `Count`, `niceNumber`, `toDecimalUnitString`.
- Control flow: Values are scaled by 1000 or 1024 until below 0.9 of the next unit, formatted with one decimal place, and trimmed. `BytesString` selects base-2 formatting when `KOPIA_BYTES_STRING_BASE_2` parses true.
- State and persistence: Reads an environment variable; otherwise stateless.
- Dependencies and integration points: Used by notification templates and UI/reporting code.
- Risks and edge cases: Threshold choices intentionally produce values like `0.9 KB`; environment selection can make output process-dependent.
- Test signals: `units_test.go` covers many boundary cases and env selection.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/units/units.go -->
