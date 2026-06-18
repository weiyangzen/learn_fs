<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvknha/vsha2ms.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvknha/vsha2ms.vv.yaml

## Purpose
`vsha2ms.vv.yaml` describes the `Zvknha` SHA-2 message-schedule helper instruction.

## Important APIs, Types, And Functions
Its assembly is `vd, vs2, vs1`, fixed match `1011011----------010-----1110111`, and variables are `vs2`, `vs1`, and `vd`. Access is all modes `always`.

## Control Flow, State, Dependencies, Risks, And Tests
The file is converted into a generated `Insn` with three operand fields. Runtime decode uses the generated template; there is no YAML state. Dependencies are the RISC-V generator and runtime descriptor package. Risks include absent SHA schedule semantics, no element-width constraints, and overlap with other SHA helper masks. Tests should check generated presence, field order, opcode distinction from `vsha2ch`/`vsha2cl`, and parse extraction of all three fields.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvknha/vsha2ms.vv.yaml -->
