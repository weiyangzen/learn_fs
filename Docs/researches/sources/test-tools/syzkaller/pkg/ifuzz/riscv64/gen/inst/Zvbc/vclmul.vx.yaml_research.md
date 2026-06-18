<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmul.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmul.vx.yaml

## Purpose
`vclmul.vx.yaml` is the `Zvbc` vector-scalar carry-less multiply descriptor. Its assembly `vd, vs2, xs1, vm` distinguishes it from the vector-vector form by using an integer scalar operand.

## Important APIs, Types, And Functions
The descriptor is consumed by the RISC-V generator as data. Its fixed match is `001100-----------110-----1010111`; declared variable ranges are `vm` 25-25, `vs2` 24-20, `xs1` 19-15, and `vd` 11-7. `data_independent_timing` is true, and S/U/VS/VU access is always allowed.

## Control Flow, State, Dependencies, Risks, And Tests
Generation turns the match pattern into a mask/opcode pair and serializes an `Insn` with these fields into `generated/insns.go`. Runtime decode then depends on the generated template order and `(value & OpcodeMask) == Opcode`. The YAML has no local state; persistence is generated Go source. Dependencies are the unified-db schema, YAML unmarshalling, the `serializer` package, and the `riscv64.Insn` type. Risks center on scalar field naming, ignored extension constraints, and empty semantic text. Test signals should include generated-table checks for `xs1`, `.vx`/.`vv` opcode separation, and decode samples that vary `vm`, `vs2`, `xs1`, and `vd` while preserving fixed bits.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmul.vx.yaml -->
