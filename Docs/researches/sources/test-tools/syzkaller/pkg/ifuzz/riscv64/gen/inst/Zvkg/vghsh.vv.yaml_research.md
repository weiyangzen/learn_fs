<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkg/vghsh.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkg/vghsh.vv.yaml

## Purpose
`vghsh.vv.yaml` describes the `Zvkg` vector GHASH instruction. It provides ifuzz with a vector-vector crypto descriptor for GHASH state update style operations.

## Important APIs, Types, And Functions
The descriptor declares assembly `vd, vs2, vs1`, match `1011001----------010-----1110111`, and fields `vs2` 24-20, `vs1` 19-15, and `vd` 11-7. There is no `vm` variable in this encoding. Access is always allowed in S/U/VS/VU, and `data_independent_timing` is true.

## Control Flow, State, Dependencies, Risks, And Tests
Generation builds a static descriptor with `OpcodeMask` reflecting the fixed vector-crypto opcode and fields for the three vector registers. Runtime state is limited to the registered generated table. Integration points are `generated/insns.go`, `riscv64.Register`, and `ParseInsn`. Risks include missing crypto semantic modeling, no enforcement of vector element group constraints, and the generator ignoring extension grouping and timing metadata. Tests should assert absence of `vm`, correct field names and lengths, generated opcode/mask stability, and decode separation from `vgmul.vv`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkg/vghsh.vv.yaml -->
