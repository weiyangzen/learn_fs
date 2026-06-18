# sources/storage-engines/foundationdb/fdbclient/JsonBuilder.cpp

## Purpose
`JsonBuilder.cpp` implements small JSON-builder helpers used by status and management output. It creates standard message objects and coerces permissive ASCII numeric strings into JSON-valid numeric spellings.

## Important APIs, Types, And Functions
`JsonBuilder::makeMessage()` returns a `JsonBuilderObject` with `name` and `description`. `JsonBuilder::coerceAsciiNumberToJSON()` accepts a character span and destination buffer, normalizes signs, leading zeroes, leading/trailing decimal points, exponents, and `inf`, and returns the number of bytes written or zero on invalid input.

## Control Flow
`coerceAsciiNumberToJSON()` exits immediately for empty input or a bare minus. It maps `inf` to `1e99`, skips leading zeroes, inserts a leading zero before a leading decimal point, writes digits and at most one decimal point, normalizes missing fractional or exponent digits to `0`, accepts optional exponent signs, and stops parsing once the numeric prefix is complete.

## State And Persistence Behavior
The file is stateless and performs no persistence. Callers provide the destination buffer, which must have at least `len + 3` bytes available because normalization may expand inputs such as `.e`.

## Dependencies And Integration Points
It depends on `fdbclient/JsonBuilder.h`, `JsonBuilderObject`, C string helpers, and `isdigit`. It is used by code that needs JSON-compatible status values even when internal status strings contain abbreviated or non-standard numeric forms.

## Risks And Edge Cases
The function accepts and returns the valid numeric prefix even if extra non-numeric suffix bytes remain after a parsed number. It only recognizes lowercase `inf`, not `+inf`, `-inf`, `nan`, or uppercase variants. The caller is responsible for destination capacity and null termination if needed; the function reports byte count, not a C string contract.

## Test Signals
Relevant tests should cover empty strings, signs, zero normalization, `.`, `.e`, decimal/exponent forms, suffix truncation, `inf`, invalid `i...` strings, and buffer sizing. No local `TEST_CASE` is present in this file.
