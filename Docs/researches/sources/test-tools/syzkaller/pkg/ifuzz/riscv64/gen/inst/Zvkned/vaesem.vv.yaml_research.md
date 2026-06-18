<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesem.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesem.vv.yaml

## Purpose
`vaesem.vv.yaml` describes the vector-vector AES encrypt middle round for `Zvkned`.

## Important APIs, Types, And Functions
It has match `1010001-----00010010-----1110111` and variable ranges for `vs2` and `vd`. The YAML name and `kind` drive generated instruction naming and inclusion.

## Control Flow, State, Dependencies, Risks, And Tests
The descriptor is read by the generator, serialized into `generated/insns.go`, and consumed through init-time registration. No local state persists. The important dependency is the simple 32-bit match parser, which rejects non-`0`/`1`/`-` characters and malformed ranges. Risks include overlap with other AES descriptors and missing semantic validation. Tests should check generated table presence, opcode separation from final/decrypt forms, operand extraction, and decode consistency.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesem.vv.yaml -->
