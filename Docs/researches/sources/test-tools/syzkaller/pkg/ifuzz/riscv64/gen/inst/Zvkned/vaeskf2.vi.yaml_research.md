<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaeskf2.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaeskf2.vi.yaml

## Purpose
`vaeskf2.vi.yaml` describes the second `Zvkned` AES key-schedule immediate descriptor.

## Important APIs, Types, And Functions
The descriptor uses match `1010101----------010-----1110111`, variables `vs2`, `imm`, and `vd`, and assembly `vd, vs2, imm`. The generator emits `imm` as a five-bit operand field.

## Control Flow, State, Dependencies, Risks, And Tests
The file follows the normal YAML-to-`Insn` path and has no independent runtime state. It integrates through the generated descriptor table and `ParseInsn`. Risks are invalid immediate generation, ignored key-schedule round semantics, and fixed-bit confusion with `vaeskf1.vi`. Tests should verify generated presence, field order, immediate extraction, and opcode difference between the two key-schedule forms.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaeskf2.vi.yaml -->
