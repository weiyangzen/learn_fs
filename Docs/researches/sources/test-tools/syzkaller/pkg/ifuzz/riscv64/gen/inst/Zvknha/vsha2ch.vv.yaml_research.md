<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvknha/vsha2ch.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvknha/vsha2ch.vv.yaml

## Purpose
`vsha2ch.vv.yaml` describes the `Zvknha` SHA-2 choose helper instruction in vector-vector form.

## Important APIs, Types, And Functions
The file declares assembly `vd, vs2, vs1`, match `1011101----------010-----1110111`, and variables `vs2`, `vs1`, and `vd`. There is no mask field. Access modes are all `always`.

## Control Flow, State, Dependencies, Risks, And Tests
The generator emits a three-field `Insn` and the runtime parser later extracts operands by bit ranges. The YAML has no persistence beyond generated source. Integration is through the generated RISC-V package and `iset` registration. Risks include lack of SHA-2 semantic modeling, no vector shape constraints, and confusion with `vsha2cl.vv` or `vsha2ms.vv` if fixed bits drift. Tests should verify field layout, generated opcode/mask, and decode separation across the three SHA-2 helpers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvknha/vsha2ch.vv.yaml -->
