<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmul.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmul.vv.yaml

## Purpose
`vclmul.vv.yaml` describes the `Zvbc` vector carry-less multiply instruction in vector-vector form. It gives ifuzz a descriptor for generating and decoding the base low-part polynomial multiply opcode.

## Important APIs, Types, And Functions
The consumed fields are `kind: instruction`, `name: vclmul.vv`, assembly `vd, vs2, vs1, vm`, match `001100-----------010-----1010111`, and variables `vm`, `vs2`, `vs1`, and `vd`. The file marks all privilege modes as `always` and declares data-independent timing, but the current generator uses only U/VU access for `Priv`.

## Control Flow, State, Dependencies, Risks, And Tests
During generation, the 32-bit match contributes fixed opcode bits while each YAML location becomes one `riscv64.InsnField`. The descriptor persists only via the generated `Insn` table; there is no direct runtime state. It integrates with vector-crypto descriptors near the tail of `generated/insns.go`, with `Register` appending the table to the `iset` registry. Risks include loss of crypto-extension metadata, no semantic validation from the empty `operation()` block, and possible decode ambiguity if future descriptors share the same fixed mask. Tests should verify that `vclmul.vv` appears with `OpcodeMask` derived from the fixed match bits, that `vm` is a one-bit field, and that `ParseInsn` recognizes representative encodings without confusing it with `vclmulh.vv`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmul.vv.yaml -->
