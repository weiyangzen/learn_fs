<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbb/vwsll.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbb/vwsll.vx.yaml

## Purpose
`vwsll.vx.yaml` describes the `Zvbb` vector-scalar widening shift-left logical instruction `vwsll.vx`. Its assembly form is `vd, vs2, xs1, vm`, so it pairs a vector source with an integer scalar shift operand.

## Important APIs, Types, And Functions
The descriptor feeds the same `instYAML` path as other RISC-V YAML files. The generator consumes the instruction name, 32-bit match string `110101-----------100-----1010111`, and variables `vm` at bit 25, `vs2` at bits 24-20, `xs1` at bits 19-15, and `vd` at bits 11-7. Access is allowed in S/U/VS/VU modes.

## Control Flow, State, Dependencies, Risks, And Tests
`gen.go` walks this file, parses fixed `1`/`0` bits into `OpcodeMask`/`Opcode`, expands variable locations into `InsnField` entries, and serializes the resulting `Insn` into `generated/insns.go`. The YAML itself has no mutable state or persistence beyond that generated descriptor. Runtime integration is through global RISC-V registration and `ParseInsn` scanning templates by mask. The important risk is operand-shape correctness: a mistaken `xs1` field would make the scalar form collide semantically with `vwsll.vv`, even though decode would still match an opcode. The generator also ignores `data_independent_timing` and the empty operation body. Tests should compare the `.vx` opcode against the `.vv` form, verify the `xs1` field name and position, and confirm fixed bits survive encode/decode.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbb/vwsll.vx.yaml -->
