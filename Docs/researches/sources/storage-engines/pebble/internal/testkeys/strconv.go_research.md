# sources/storage-engines/pebble/internal/testkeys/strconv.go

## Purpose
This file provides an allocation-avoiding `[]byte` variant of `strconv.ParseUint` for the `testkeys` package. It is copied from go4.org/strconv and is used when parsing timestamp suffixes out of byte slices.

## Important APIs, Types, and Functions
`parseUintBytes(s, base, bitSize)` supports base validation, base auto-detection for `0`, `0x`, and leading-zero octal, digit scanning, overflow checks, and returns `*strconv.NumError` on failure. `cutoff64(base)` computes the overflow threshold for multiplication.

## Control Flow and State
The parser validates inputs, determines base, iterates over bytes, maps ASCII digits and letters to values, checks value range and overflow, and returns parsed `uint64`. It uses `goto Error` to share construction of `NumError`. There is no persistent state.

## Dependencies and Integration
It depends on `strconv` and Cockroach errors. `testkeys.Compare` and validation use it through timestamp suffix parsing to avoid converting suffix byte slices into strings in hot test paths.

## Risks and Edge Cases
The function intentionally mirrors older strconv behavior and must stay compatible with expected `NumError` semantics. It handles ASCII digits only. Overflow behavior sets `n` to max uint64 before returning range error, matching standard library style.

## Test Signals
There is no direct test for this file, but `testkeys_test.go` exercises suffix comparison and comparer validation, indirectly covering successful decimal parses and invalid-key validation.
