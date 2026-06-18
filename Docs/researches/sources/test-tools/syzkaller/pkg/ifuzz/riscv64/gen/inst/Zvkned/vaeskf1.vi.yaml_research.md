<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaeskf1.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaeskf1.vi.yaml

## Purpose
`vaeskf1.vi.yaml` describes the `Zvkned` AES key-schedule helper form with an immediate operand. It contributes the first key-schedule descriptor to ifuzz.

## Important APIs, Types, And Functions
The assembly is `vd, vs2, imm`, match `1000101----------010-----1110111`, and variables are `vs2` 24-20, `imm` 19-15, and `vd` 11-7. Access is unrestricted for generated privilege classification.

## Control Flow, State, Dependencies, Risks, And Tests
The generator parses the immediate field as a normal five-bit `InsnField`; it does not model valid round ranges. Runtime parse extracts `vs2`, `imm`, and `vd` from any matching value. State is limited to generated Go source and global registration. Risks include invalid immediate values being fuzzed, ignored AES key-schedule semantics, and possible confusion with `vaeskf2.vi`. Tests should assert field names, immediate width, opcode separation from `vaeskf2.vi`, and representative decode behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaeskf1.vi.yaml -->
