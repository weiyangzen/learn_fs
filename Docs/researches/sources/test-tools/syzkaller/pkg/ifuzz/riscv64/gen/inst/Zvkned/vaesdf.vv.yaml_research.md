<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdf.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdf.vv.yaml

## Purpose
`vaesdf.vv.yaml` describes the `Zvkned` vector AES decrypt final round vector-vector encoding. It sits beside the `.vs` form with a different fixed opcode prefix.

## Important APIs, Types, And Functions
The file declares match `1010001-----00001010-----1110111`, variables `vs2` and `vd`, and S/U/VS/VU access as `always`. Its operation block is empty, so the generator only persists encoding metadata.

## Control Flow, State, Dependencies, Risks, And Tests
`gen.go` accepts the file as a 32-bit instruction and emits an `Insn` that `Register` later installs globally. There is no local persistence beyond generated Go. Dependencies are YAML unmarshalling, unified-db schema conventions, and the RISC-V ifuzz runtime. Risks include `.vv`/`.vs` confusion, loss of AES final-round semantics, and no validation of architectural operand restrictions. Tests should assert generated presence, correct two-register field list, opcode difference from `vaesdf.vs`, and successful `ParseInsn` extraction of `vs2`/`vd`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdf.vv.yaml -->
