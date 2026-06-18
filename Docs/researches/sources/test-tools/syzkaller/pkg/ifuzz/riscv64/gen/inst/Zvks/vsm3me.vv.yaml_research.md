<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm3me.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm3me.vv.yaml

## Purpose
`vsm3me.vv.yaml` describes the SM3 message-expansion helper. It is also defined by `Zvksh` while stored under the `Zvks` descriptor directory.

## Important APIs, Types, And Functions
The match is `1000001----------010-----1110111`, with variables `vs2`, `vs1`, and `vd`. Assembly is `vd, vs2, vs1`.

## Control Flow, State, Dependencies, Risks, And Tests
The RISC-V generator emits one three-field descriptor and the runtime parser later extracts all three register operands. No state exists in the YAML. Risks include extension-directory mismatch for tooling that assumes path equals `definedBy`, ignored SM3 semantics, and no operand legality checking. Tests should cover generated presence, field order, opcode difference from `vsm3c.vi`, and decode round trips.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm3me.vv.yaml -->
