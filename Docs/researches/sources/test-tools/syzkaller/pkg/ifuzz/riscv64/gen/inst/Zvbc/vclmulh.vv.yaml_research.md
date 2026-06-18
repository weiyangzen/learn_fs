<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmulh.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmulh.vv.yaml

## Purpose
`vclmulh.vv.yaml` describes the high-part vector-vector carry-less multiply instruction from `Zvbc`. It complements `vclmul.vv` by selecting the high result half through different fixed opcode bits.

## Important APIs, Types, And Functions
The key consumed fields are `name: vclmulh.vv`, assembly `vd, vs2, vs1, vm`, match `001101-----------010-----1010111`, and variables `vm`, `vs2`, `vs1`, and `vd` with standard vector arithmetic positions. Access modes are all `always`.

## Control Flow, State, Dependencies, Risks, And Tests
`gen.go` treats this as a valid 32-bit instruction, builds mask/opcode values, parses each `hi-lo` location into `InsnField`, and writes an `Insn` literal. There is no runtime state in the YAML; generated registration is the only persistent behavior. Integration is with the RISC-V generated package, `riscv64.ParseInsn`, and generic ifuzz decode checks. The main risks are collision with `vclmul.vv` if the high/low fixed bits drift, ignored semantic and extension data, and lack of operand constraints beyond raw bit extraction. Tests should assert separate generated opcodes for `vclmul` and `vclmulh`, correct field order, and successful decode of representative high-part encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmulh.vv.yaml -->
