<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmulh.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmulh.vx.yaml

## Purpose
`vclmulh.vx.yaml` is the vector-scalar high-part carry-less multiply descriptor for `Zvbc`. It exposes the scalar `xs1` operand variant to the RISC-V ifuzz table.

## Important APIs, Types, And Functions
The generator consumes match `001101-----------110-----1010111` and variables `vm` bit 25, `vs2` bits 24-20, `xs1` bits 19-15, and `vd` bits 11-7. Its access block keeps it non-privileged for ifuzz purposes.

## Control Flow, State, Dependencies, Risks, And Tests
The descriptor is read, unmarshaled, validated for 32-bit match length, and converted into an `Insn` literal with fixed mask/opcode and variable fields. Runtime behavior is indirect through generated registration; `Encode` emits `AsUInt32`, while parsing extracts operands by `extractBits`. Risks include the generator ignoring architecture-level scalar/vector constraints, data-independent timing, and future schema fields, plus decode ambiguity if masks overlap. Tests should cover presence in `generated/insns.go`, the `xs1` field, high-vs-low opcode distinction, and parse/encode stability for values that vary each declared operand bitfield.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmulh.vx.yaml -->
