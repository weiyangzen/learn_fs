<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/text.go -->
# sources/security-integrity/libcap/cap/text.go

## Purpose
Text conversion for capability values and sets, compatible with libcap text syntax.

## Important APIs, Types, And Functions
Defines `Value.String`, `FromName`, `Set.String`, `FromText`, `ErrBadText`, `combos`, and helper `histo`.

## Control Flow
String generation builds a histogram of flag combinations to choose a compact background state, emits differences for named bits, then appends numeric unnamed bits. Parsing tokenizes space-separated chunks, supports `all`, named/numeric values, `=`, `+`, `-`, and flag letters `eip`, applying each operation to a new `Set`.

## State And Persistence Behavior
Only in-memory `Set` state is read or mutated. Parsing returns a new set; stringification locks an existing set for reading.

## Dependencies And Integration Points
Uses generated name maps from `names.go` and flag operations from `flags.go`. Used by examples, tests, import/export diagnostics, and user APIs.

## Risks And Edge Cases
The parser is intentionally strict and returns `ErrBadText` for malformed tokens. Canonical output may change compactness over releases but must remain parse-compatible.

## Test Signals
Signals are exact text tests, examples, and import/export/text round trips.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/text.go -->
