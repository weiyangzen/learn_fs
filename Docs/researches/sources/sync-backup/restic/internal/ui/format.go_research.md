<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/format.go -->
# sources/sync-backup/restic/internal/ui/format.go

## Purpose
Provides shared UI formatting/parsing helpers for sizes, percentages, durations, JSON, display widths, quoting, and truncation.

## Important APIs and Control Flow
`FormatBytes`, `FormatPercent`, `FormatDuration`, `FormatSeconds`, `ParseBytes`, `ToJSONString`, `DisplayWidth`, `Quote`, `Truncate`, and `wideRune` are central. The functions format binary units, clamp percentages at 100%, parse B/K/M/G/T suffixes with overflow checks, JSON-encode statuses, and handle terminal cell widths for Unicode. Control flow is deterministic formatting/parsing with early returns for zero denominators, invalid sizes, non-printable strings, and width overflow.

## State, Persistence, Dependencies, and Integration
No persistent state. Dependencies include JSON, `math/bits`, `strconv`, Unicode helpers, and `golang.org/x/text/width`; integration spans backup/restore text and JSON printers.

## Risks and Test Signals
Risks are terminal width ambiguity, overflow parsing, invalid UTF-8 quoting, and truncating within multi-byte runes. Tests cover bytes, percentages, parsing invalid/valid sizes, display width, quote, truncate, and benchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/format.go -->
