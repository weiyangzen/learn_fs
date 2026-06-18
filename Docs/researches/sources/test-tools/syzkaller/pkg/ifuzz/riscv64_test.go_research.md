<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64_test.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64_test.go

## Purpose
`riscv64_test.go` contains package-level tests and debug print helpers for the RISC-V ifuzz backend. It validates that representative RISC-V opcodes can be parsed and decoded through the registered architecture set.

## Important APIs, Types, And Functions
`PrintInsnRv` formats a parsed `riscv64.Insn` with operand names, widths, and values. `parseAndPrintRv` calls `riscv64.ParseInsn`. `TestSomethingRv` parses a handful of hard-coded instruction words. `TestSumRv` parses hex/opcode pairs with assembly comments. `decodeRvText` repeatedly calls `InsnSet.Decode` over byte slices. `TestDecodeSamplesRv` hex-decodes sample byte strings and decodes them through `iset.Arches["riscv64"]`.

## Control Flow
The tests rely on generated package registration having populated `iset.Arches`. Decode samples are little-endian byte streams; `decodeRvText` advances by the size returned from `Decode`, which should be 4 for every RISC-V instruction. Parse helpers print decoded fields but generally do not assert instruction names.

## State and Dependencies
The tests depend on `encoding/binary`, `encoding/hex`, `fmt`, `strconv`, `testing`, `pkg/ifuzz/iset`, and `pkg/ifuzz/riscv64`. They mutate no persistent state, but they rely on global architecture registration.

## Risks and Test Signals
The tests are useful smoke coverage for parsing and registered decode, but many checks are print-only and would not fail on wrong names if parsing succeeds. They cover base integer, CSR/time, trap, multiplication/division, and memory-like samples, not the vector crypto/BF16 descriptors in this work item. Stronger tests would assert returned names and operands, include unknown/short input errors, and add representative generated vector-extension opcodes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64_test.go -->
