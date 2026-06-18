<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdm.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdm.vs.yaml

## Purpose
`vaesdm.vs.yaml` describes the `Zvkned` vector AES decrypt middle-round instruction in `.vs` form. It contributes one AES decrypt-middle opcode to the generated RISC-V table.

## Important APIs, Types, And Functions
The match string is `1010011-----00000010-----1110111`; variables are `vs2` bits 24-20 and `vd` bits 11-7. Access is allowed in all listed privilege modes and data-independent timing is true.

## Control Flow, State, Dependencies, Risks, And Tests
The descriptor is parsed by `gen.go`, serialized into `generated/insns.go`, and consumed at runtime by `ParseInsn` through mask matching. It has no own state or persistence. Integration depends on the generated package being imported so `init` calls `Register`. Risks include middle-vs-final round fixed-bit mistakes, ignored AES semantic details, and no generated operand legality checks. Test signals should include opcode comparison with `vaesdf.vs`, `.vv`/`.vs` separation, generated field count checks, and representative decode samples.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdm.vs.yaml -->
