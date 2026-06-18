<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesem.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesem.vs.yaml

## Purpose
`vaesem.vs.yaml` describes the `Zvkned` vector AES encrypt middle round in `.vs` form.

## Important APIs, Types, And Functions
The file provides match `1010011-----00010010-----1110111`, fields `vs2` 24-20 and `vd` 11-7, and access metadata that maps to non-privileged generated output.

## Control Flow, State, Dependencies, Risks, And Tests
`gen.go` uses the YAML to emit one generated `Insn`; the descriptor has no runtime state except generated registration. Its integration points are the generated table, `riscv64.ParseInsn`, and generic ifuzz decode tests. Risks include wrong AES round classification due to fixed-bit mistakes, ignored data-independent timing, and absent semantic checks. Tests should verify the generated `vaesem.vs` entry is distinct from `vaesef.vs` and `vaesdm.vs`, contains exactly `vs2` and `vd`, and decodes representative values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesem.vs.yaml -->
