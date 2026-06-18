# sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/call_selector_test.go

## Purpose
This file tests the filename-pattern matching helper used by trace-to-program syscall selection.

## Important APIs, types, and functions
- `TestMatchFilename` constructs a bare `selectorCommon` and tests `matchFilename` over exact paths, `#` digit placeholders, NUL-terminated syzkaller strings, length mismatches, and mismatched characters.

## Control flow
Each table row passes two byte slices to `matchFilename` and verifies both the boolean match and extracted device ID. Multiple `#` placeholders accumulate digits into one decimal ID.

## State and persistence behavior
No persistent state. The selector has no target or return cache because `matchFilename` is self-contained.

## Dependencies and integration points
Tests `selectorCommon.matchFilename`, which is used by both open-family and default pointer-buffer matching in `call_selector.go`.

## Risks and edge cases
Coverage does not include non-ASCII paths, more complex NUL placement, empty-equal paths, or invalid digit extraction overflow. It also does not test callers that mutate syscall args after a match.

## Test signals
Good focused signal for the pattern matcher's intended behavior. Broader call selection remains undertested.
