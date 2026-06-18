<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdf.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdf.vs.yaml

## Purpose
`vaesdf.vs.yaml` describes the `Zvkned` vector AES decrypt final round in vector-scalar-group style form. Its assembly lists `vd, vs2`, with remaining selector bits fixed.

## Important APIs, Types, And Functions
The descriptor uses match `1010011-----00001010-----1110111` and variables `vs2` 24-20 and `vd` 11-7. It has unrestricted access and data-independent timing metadata.

## Control Flow, State, Dependencies, Risks, And Tests
Generation parses the descriptor into a two-field static `Insn`; no YAML state exists after generation. It integrates with the generated RISC-V package and the runtime mask-matching parser. Risks are primarily semantic loss: final-round AES behavior, vector grouping constraints, and timing flags are not emitted. Because many AES descriptors differ only in fixed bits, mask/opcode drift can silently decode as the wrong round form. Tests should compare `.vs` and `.vv` AES decrypt-final entries, confirm two-field layout, and decode representative opcodes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdf.vs.yaml -->
