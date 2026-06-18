<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/util.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/util.go

## Purpose
`util.go` contains the RISC-V backend's bitfield extraction helper used when parsed instructions populate operand values.

## Important APIs, Types, And Functions
The single function is `extractBits(from uint32, start, size uint) uint32`. `start` is the high bit index in little-endian bit numbering and `size` is the field width. The function builds a mask `(1 << size) - 1`, shifts `from` right by `start - size + 1`, and returns the masked value.

## Control Flow
There is no branching. `riscv64.Insn.initFromValue` calls this helper for every `InsnField` in a matched template, appending extracted operands in field order.

## State, Dependencies, Integration, Risks, And Tests
The helper is pure and has no dependencies or persistence. It integrates with `ParseInsn` and generated field definitions, including split immediates and vector operands. Risks include unsigned arithmetic underflow if callers pass `size > start+1`, and shift/mask corner cases for wide fields. Current use is safe for generated `hi-lo` ranges where `hi >= lo`, but malformed manual descriptors could panic or produce invalid shifts. `util_test.go` covers zero-size fields, single-bit extraction, mid-word ranges, and RISC-V register fields from an encoded `add` sample.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/util.go -->
