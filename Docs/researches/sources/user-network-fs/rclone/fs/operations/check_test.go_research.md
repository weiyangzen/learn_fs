# sources/user-network-fs/rclone/fs/operations/check_test.go

## Purpose
`check_test.go` validates the tree comparison, download comparison, checksum-file parsing, checksum verification, and path normalization behavior implemented in `check.go`.

## Important APIs, types, and functions
- `testCheck` is a shared scenario runner for `operations.Check` and `operations.CheckDownload`.
- `TestCheck`, `TestCheckDownload`, and `TestCheckSizeOnly` exercise the main comparison modes.
- `TestCheckFsError` validates error propagation from failing filesystems.
- `TestCheckEqualReaders` unit-tests byte-stream comparison.
- `TestParseSumFile` validates checksum-file parser acceptance and rejection cases.
- `testCheckSum`, `TestCheckSum`, and `TestCheckSumDownload` validate `CheckSum` with backend hash reads and downloaded hash calculation.
- `TestApplyTransforms` verifies Unicode normalization and case-folding behavior for checksum filenames.

## Control flow
The tests build local/remote fixture trees with `fstest.NewRun`, then call check functions with every output writer backed by a `bytes.Buffer`. They capture log output, inspect accounting counters for errors and checks, and compare sorted report lines so concurrent check ordering does not make tests flaky. Checksum tests create a data subfilesystem, write a `test.sum` file, update file contents and sums across scenarios, and assert the expected sigil stream.

## State and persistence behavior
The tests create and mutate temporary local and remote test files. They reset `accounting.GlobalStats()` between scenarios and temporarily toggle config flags such as `SizeOnly`, `NoUnicodeNormalization`, and `IgnoreCaseSync`, restoring where needed. No persistent repository state is changed.

## Dependencies and integration points
The file uses rclone `fstest`, `fs`, `accounting`, `hash`, `operations`, `readers.ErrorReader`, `bilib.CaptureOutput`, `testify`, and Unicode normalization helpers. It provides coverage for `check.go` plus shared helpers in `operations.go` such as `CheckHashes` and output counting.

## Risks and edge cases
The expected outputs encode the meaning of check sigils and the distinction between missing-on-source and missing-on-destination. Tests account for concurrency by sorting lines. Unicode tests skip when the backend cannot preserve the requested filename encoding. Size-only tests intentionally accept changed content when sizes match.

## Test signals
The file is the main regression signal for check/report behavior: matching files increment check counts, differences increment error counts, one-way mode suppresses destination-only errors, malformed sum lines are ignored, duplicate sum entries are rejected, mixed-case digests are normalized, and checksum names can be matched through NFC normalization and case folding.
