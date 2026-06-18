<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/util_test.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/util_test.go

## Purpose
`util_test.go` verifies the RISC-V bit extraction helper that underpins operand decoding from generated templates.

## Important APIs, Types, And Functions
It defines helper `extractBitsOne(t, from, start, size, expect)` and test `TestExtractBits`. The helper calls `extractBits` and fails with a formatted message when the result differs from expectation.

## Control Flow
`TestExtractBits` checks zero-width extraction on zero and all-ones values, iterates every bit position 0 through 31 for one-bit extraction, verifies several ranges from `0xf0f0f0f0`, and then validates `xs2`, `xs1`, and `xd` extraction from a concrete RISC-V R-type `add`-shaped value.

## State, Dependencies, Integration, Risks, And Tests
The test uses only Go's `testing` package and local helper code. It has no persistence. It integrates directly with `util.go` and indirectly protects `ParseInsn` operand extraction. The main gap is that it does not test full-width 32-bit extraction, invalid `start`/`size` combinations, split-field recomposition, or generated descriptor parsing end to end. Its existing signals are useful for off-by-one errors in the `start - size + 1` shift formula and for confirming that generated field conventions match RISC-V bit positions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/util_test.go -->
