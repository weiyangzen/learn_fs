# sources/storage-engines/sqlite/tool/checkSpacing.c

## Purpose
`checkSpacing.c` is a source-format checker that reports tab characters, optional carriage returns, optional trailing spaces, and blank lines at EOF. It is a lightweight style gate for SQLite source files.

## Important APIs, Types, and Functions
Flags `CR_OK` and `WSEOL_OK` control whether carriage returns and whitespace-at-end-of-line are tolerated. `checkSpacing()` opens a file in binary mode, scans lines with `fgets()`, tracks tabs, spaces, line numbers, and last non-space line, and prints findings. `main()` parses `--crok`, `--wseol`, and `--help`.

## Control Flow
The default allows trailing spaces but reports tabs, carriage returns, and trailing blank lines. `--crok` suppresses carriage-return reports. `--wseol` enables trailing-space reports by clearing `WSEOL_OK`. Non-option arguments are checked independently.

## State and Persistence
The tool has no persistent state and does not modify files. It reports all findings to stdout and returns zero regardless of violations.

## Dependencies and Integration Points
It depends only on the C runtime. It can be integrated into make/test scripts, though callers must parse output because the exit status does not indicate failure.

## Risks
Lines longer than 1999 bytes are read in fragments, which can affect trailing whitespace and line accounting. Because violations do not change the exit code, CI must treat non-empty output as failure. The default of allowing trailing spaces may surprise users expecting strict style checks.

## Test Signals
Use files containing tabs, CRLF line endings, trailing spaces, final blank lines, long lines, missing files, and combinations of `--crok` and `--wseol`. Expected output should include filename and line number.
