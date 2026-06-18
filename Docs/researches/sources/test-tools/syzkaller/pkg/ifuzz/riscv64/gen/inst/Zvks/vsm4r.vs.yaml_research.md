<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm4r.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm4r.vs.yaml

## Purpose
`vsm4r.vs.yaml` describes an SM4 round instruction in `.vs` form, defined by `Zvksed`.

## Important APIs, Types, And Functions
The descriptor provides match `1010011-----10000010-----1110111` and variables `vs2` and `vd`. The generator uses these to create a two-field non-privileged `Insn`.

## Control Flow, State, Dependencies, Risks, And Tests
The file follows the standard YAML generation path and has no independent state. Runtime decode is mask-based after generated registration. Risks include `.vs`/`.vv` opcode confusion, ignored SM4 semantic constraints, and loss of extension metadata. Tests should assert correct two-field layout, opcode difference from `vsm4r.vv`, and successful representative decode.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm4r.vs.yaml -->
