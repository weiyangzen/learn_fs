<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesz.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesz.vs.yaml

## Purpose
`vaesz.vs.yaml` describes `vaesz.vs`, the `Zvkned` vector AES round-zero instruction. Its long name explicitly identifies it as "Vector AES round zero".

## Important APIs, Types, And Functions
The descriptor provides match `1010011-----00111010-----1110111`, variables `vs2` and `vd`, and always-allowed access modes. It is a two-field descriptor like many AES round forms.

## Control Flow, State, Dependencies, Risks, And Tests
Generation serializes this YAML into a generated `Insn`; runtime registration and parsing are inherited from the RISC-V backend. The file has no local state. Risks include fixed-bit overlap with other AES `.vs` forms, ignored AES round-zero semantics, and no operation snippet to compare against architecture behavior. Tests should assert the generated entry exists with only `vs2` and `vd`, is distinct from decrypt/encrypt final/middle forms, and decodes representative round-zero opcodes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesz.vs.yaml -->
