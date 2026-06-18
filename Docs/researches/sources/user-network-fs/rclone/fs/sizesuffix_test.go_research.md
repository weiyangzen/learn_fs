# sources/user-network-fs/rclone/fs/sizesuffix_test.go

## Purpose
This file verifies parsing, formatting, scanning, and JSON behavior for `SizeSuffix`.

## Important APIs, Types, and Functions
- Interface assertions verify `SizeSuffix` satisfies rclone flag interfaces.
- `TestSizeSuffixString`, `TestSizeSuffixByteUnit`, and `TestSizeSuffixBitRateUnit` check formatting.
- `TestSizeSuffixSet` checks accepted and rejected string syntax.
- `TestSizeSuffixScan` verifies `fmt.Sscan` integration.
- `TestSizeSuffixUnmarshalJSON` checks string and integer JSON inputs.

## Control Flow
The tests use table-driven cases, instantiate a fresh `SizeSuffix`, call the target method, assert expected error presence, and compare int64/string results.

## State and Persistence
No persistent or global state is touched.

## Dependencies and Integration Points
It uses `encoding/json`, `fmt`, and `testify`. The tests document behavior relied on by config, flags, and RC JSON option handling.

## Risks and Edge Cases
The tests explicitly reject `1MB` while accepting `1M` and `1MiB`, preserving the binary-only suffix contract. They do not cover overflow or NaN/Inf float parsing.

## Test Signals
Coverage is strong for normal values, off/negative rendering, invalid suffixes, empty strings, negative inputs, and JSON numeric fallback.
