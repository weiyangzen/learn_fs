<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesef.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesef.vv.yaml

## Purpose
`vaesef.vv.yaml` describes the vector-vector AES encrypt final round descriptor from `Zvkned`.

## Important APIs, Types, And Functions
The relevant encoding data is match `1010001-----00011010-----1110111`, variables `vs2` and `vd`, and all access modes `always`. The empty operation block is not consumed by the current generator.

## Control Flow, State, Dependencies, Risks, And Tests
The file becomes a static `Insn` after the generator walks and parses it; registration then places the generated descriptor set under `iset.ArchRiscv64`. It has no standalone state. Risks include subtle fixed-bit drift among AES forms, ignored semantic metadata, and no operand constraints beyond raw register fields. Test signals should include generated presence, two-field decode extraction, `.vv`/`.vs` opcode difference, and parse coverage alongside `vaesem.vv`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesef.vv.yaml -->
