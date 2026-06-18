<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkg/vgmul.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkg/vgmul.vv.yaml

## Purpose
`vgmul.vv.yaml` describes the `Zvkg` vector GCM multiply instruction. It is a compact two-operand vector crypto descriptor with assembly `vd, vs2`.

## Important APIs, Types, And Functions
The fixed match is `1010001-----10001010-----1110111`. Variables are only `vs2` at bits 24-20 and `vd` at bits 11-7; bits 19-15 and other fields are fixed by the match. Access is unrestricted for the generator's privilege model.

## Control Flow, State, Dependencies, Risks, And Tests
The RISC-V generator emits one `Insn` if the 32-character match and two variable ranges parse successfully. The YAML has no state; it persists as a generated Go descriptor. At runtime, `ParseInsn` extracts only `vs2` and `vd` from matched values. Risks include accidental introduction of a variable where the architecture reserves fixed bits, ignored crypto operation semantics, and decode-order sensitivity if another descriptor overlaps the mask. Tests should verify exactly two fields, fixed reserved bits, generated presence, and successful decode of the representative opcode in the generated table.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkg/vgmul.vv.yaml -->
