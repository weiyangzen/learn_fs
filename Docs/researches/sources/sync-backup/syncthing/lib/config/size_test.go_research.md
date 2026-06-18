# sources/sync-backup/syncthing/lib/config/size_test.go

## sources/sync-backup/syncthing/lib/config/size_test.go

Purpose: Tests `Size` default parsing, size parsing, formatting, and free-space validation.

Important APIs/types/functions: `TestSizeDefaults`, `TestParseSize`, `TestFormatSI`, and `TestCheckAvailableSize`.

Control flow and state: Defaults are applied via `structutil.SetDefaults`. Parse cases cover upper/lower SI prefixes, fractions, unsupported negative numbers, arbitrary unit suffixes, percentages, empty strings, and plain numbers. Free-space cases check absolute and percentage thresholds after a simulated required allocation.

Dependencies and integration: Uses `fs.Usage` and `structutil`.

Risks and test signals: These tests document intentionally permissive units and intentionally rejected negatives, protecting disk safety behavior in folder and home free-space checks.
