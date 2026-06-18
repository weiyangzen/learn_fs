# sources/test-tools/syzkaller/pkg/ifuzz/arm64/util_test.go

## Purpose
`util_test.go` validates ARM64 bit-field extraction behavior for the parser helper in `util.go`.

## Important APIs, Types, And Functions
`extractBitsOne` is a small assertion helper that calls `extractBits` and fails the test with the input coordinates and observed value. `TestExtractBits` is the only test case and covers zero-width, single-bit, and multi-bit extraction.

## Control Flow
The test first checks that zero-size extraction returns zero for both zero and all-ones input. It then iterates bit positions 0 through 31 and verifies that extracting a one-bit field from `0xffffffff` always returns one. Finally it checks three known multi-bit slices from `0xf0f0f0f0`.

## State And Persistence Behavior
The test is pure and has no persistent state. It uses only local values and the `testing` package.

## Dependencies And Integration Points
The test is in package `arm64`, so it can call the unexported `extractBits` helper directly. It supports the generated parser path because every parsed `Insn.Operands` value is produced by this helper.

## Risks And Edge Cases
The test does not exercise invalid coordinates, full-width extraction, fields that end below their size, or fields generated from every real `InsnField`. It also uses `t.Fatalf`, so a failure stops the test at the first bad case rather than reporting all bad coordinates.

## Test Signals
This is the focused unit signal for ARM64 operand extraction. It should be run with broader ARM64 decode tests after generator changes because this test verifies only the primitive bit operation, not descriptor ordering or field metadata.
