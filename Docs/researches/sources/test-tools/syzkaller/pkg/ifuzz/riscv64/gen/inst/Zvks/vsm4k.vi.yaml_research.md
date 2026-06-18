<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm4k.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm4k.vi.yaml

## Purpose
`vsm4k.vi.yaml` describes the SM4 key-schedule helper instruction. It is defined by `Zvksed` and uses an immediate operand.

## Important APIs, Types, And Functions
The match string is `1000011----------010-----1110111`; variables are `vs2` 24-20, `imm` 19-15, and `vd` 11-7. Access is all modes `always`.

## Control Flow, State, Dependencies, Risks, And Tests
Generation emits a static `Insn` with an unconstrained five-bit immediate. Runtime integration is through the generated table and RISC-V mask matching. The YAML has no local state. Risks include invalid immediate values, ignored SM4 key-schedule semantics, and extension metadata not surviving into generated descriptors. Tests should verify field names, immediate width, generated opcode, and separation from `vsm4r` round descriptors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm4k.vi.yaml -->
