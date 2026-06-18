# sources/storage-engines/pebble/internal/binfmt/hexdump.go

Purpose: Implements a compact hex dump utility with optional offsets and ASCII sidebars.

APIs and types: `HexDump(data, width, includeOffsets)` and `FHexDump(w, data, width, includeOffsets)`.

Control flow and state: Iterates data in rows of `width`, optionally prints zero-padded hex offsets, groups hex bytes every four bytes, pads incomplete rows, and prints printable ASCII or `.` for non-printable bytes.

Persistence and dependencies: Diagnostic runtime output only. Depends on `fmt`, `io`, `strconv`, and `bytes.Buffer`.

Integration points: Used by datadriven tests and binary-format debugging tools.

Risks: `width` must be positive; zero or negative width would break loop progress. Output format is test-sensitive.

Test signals: `hexdump_test.go` verifies output through datadriven cases over generated and file-backed data.
