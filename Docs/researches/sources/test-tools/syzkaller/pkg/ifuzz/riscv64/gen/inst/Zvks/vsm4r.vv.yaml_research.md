<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm4r.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm4r.vv.yaml

## Purpose
`vsm4r.vv.yaml` describes the SM4 round instruction in vector-vector form. Its `definedBy` uses `anyOf` with `Zvks` and `Zvksed`.

## Important APIs, Types, And Functions
The consumed encoding is match `1010001-----10000010-----1110111`, variables `vs2` and `vd`, and all access modes `always`. The current generator does not model the `anyOf` extension expression.

## Control Flow, State, Dependencies, Risks, And Tests
Generation serializes this as a normal two-field descriptor; runtime integration is generated registration plus `ParseInsn`. The source has no state. Risks include losing the `anyOf` extension relationship, `.vv`/`.vs` fixed-bit mixups, and no SM4 semantic validation. Tests should check generated presence, two-field layout, opcode distinction from `vsm4r.vs`, and decode coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm4r.vv.yaml -->
