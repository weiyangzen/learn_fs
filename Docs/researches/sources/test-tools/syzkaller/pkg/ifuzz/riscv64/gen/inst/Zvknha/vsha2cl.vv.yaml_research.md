<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvknha/vsha2cl.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvknha/vsha2cl.vv.yaml

## Purpose
`vsha2cl.vv.yaml` describes the `Zvknha` SHA-2 choose/low companion helper in vector-vector form.

## Important APIs, Types, And Functions
The consumed match is `1011111----------010-----1110111`; variables are `vs2` 24-20, `vs1` 19-15, and `vd` 11-7. The descriptor is non-privileged and marked data-independent timing.

## Control Flow, State, Dependencies, Risks, And Tests
Generation creates a static descriptor; runtime integration is through generated registration and mask matching. No local state persists. Risks are fixed-bit mixups among SHA-2 helpers, ignored timing/extension metadata, and no semantic validation. Tests should assert correct three-register fields, opcode separation from `vsha2ch.vv`, and decode of representative encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvknha/vsha2cl.vv.yaml -->
