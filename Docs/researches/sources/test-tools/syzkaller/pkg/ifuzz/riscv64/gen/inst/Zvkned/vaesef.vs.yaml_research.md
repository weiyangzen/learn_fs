<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesef.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesef.vs.yaml

## Purpose
`vaesef.vs.yaml` describes the `Zvkned` vector AES encrypt final round in `.vs` form.

## Important APIs, Types, And Functions
It defines match `1010011-----00011010-----1110111` and variables `vs2` 24-20 and `vd` 11-7. The generator also sees `name: vaesef.vs`, `kind: instruction`, and always-allowed U/VU access.

## Control Flow, State, Dependencies, Risks, And Tests
Generation converts the fixed bits to `OpcodeMask`/`Opcode` and writes a generated two-field `Insn`. Runtime behavior comes from registration and mask-based parsing; the YAML has no mutable state. Dependencies include unified-db YAML shape, `yaml.v3`, and the RISC-V ifuzz runtime. Risks include confusion between encrypt/decrypt and final/middle fixed-bit groups, ignored AES semantics, and absence of vector legality constraints. Tests should compare against `vaesem.vs` and `vaesdf.vs`, assert exact field layout, and run decode checks for representative encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesef.vs.yaml -->
