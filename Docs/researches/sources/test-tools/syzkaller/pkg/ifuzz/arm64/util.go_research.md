# sources/test-tools/syzkaller/pkg/ifuzz/arm64/util.go

## Purpose
`util.go` provides the bit-field extraction helper used by the ARM64 parser to recover operand values from a concrete 32-bit instruction word.

## Important APIs, Types, And Functions
`extractBits(from uint32, start, size uint) uint32` builds a mask of `size` bits and returns the field ending at bit position `start`, using the little-endian bit numbering convention documented by `InsnField.Start`.

## Control Flow
The helper computes `mask := uint32((1 << size) - 1)`, shifts the input right by `start - size + 1`, and applies the mask. `arm64.(*Insn).initFromValue` calls this once for each generated `InsnField` while `ParseInsn` constructs a parsed instruction result.

## State And Persistence Behavior
The helper is pure and stateless. It performs no allocation, mutation, or persistence. Its output is deterministic for the supplied word and field coordinates.

## Dependencies And Integration Points
`util.go` has no imports. It is tightly coupled to the generator's field layout: `gen/gen.go` emits `InsnField{Start, Length}` values from ARM64 JSON bit patterns, and `arm64.go` uses `extractBits` to populate `Insn.Operands` for diagnostics and tests.

## Risks And Edge Cases
The function assumes valid field coordinates. If `size` is greater than the integer width used by the untyped `1` expression after conversion, or if `start + 1 < size`, the shift expression can behave incorrectly or panic at runtime for invalid unsigned shift counts. Current generated fields are within 32-bit ARM64 instruction bounds. A `size` of zero returns zero in existing tests, which is useful for defensive behavior but not a real ARM64 field shape.

## Test Signals
`util_test.go` covers zero-size extraction, one-bit extraction at every bit position, and several multi-bit fields from `0xf0f0f0f0`. Parser-oriented tests in `arm64_test.go` also rely on this helper indirectly when printing decoded operands.
