<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm3c.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm3c.vi.yaml

## Purpose
`vsm3c.vi.yaml` describes an SM3 compression helper instruction. Although it lives under `gen/inst/Zvks`, its `definedBy` extension is `Zvksh`.

## Important APIs, Types, And Functions
The descriptor uses assembly `vd, vs2, imm`, match `1010111----------010-----1110111`, and variables `vs2` 24-20, `imm` 19-15, and `vd` 11-7.

## Control Flow, State, Dependencies, Risks, And Tests
Generation treats the immediate as an unconstrained five-bit `InsnField` and emits a static descriptor. The file has no state apart from generated Go output and registration. Integration is with the vector crypto tail of `generated/insns.go`. Risks include directory/extension naming mismatch, ignored SM3 immediate validity constraints, and absent semantic operation data. Tests should assert generated field layout, immediate extraction, non-privileged classification, and decode separation from SM4 key and SM3 message expansion descriptors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm3c.vi.yaml -->
