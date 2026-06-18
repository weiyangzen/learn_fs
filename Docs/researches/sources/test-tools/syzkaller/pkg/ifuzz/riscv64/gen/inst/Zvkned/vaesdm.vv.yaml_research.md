<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdm.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdm.vv.yaml

## Purpose
`vaesdm.vv.yaml` describes the vector-vector AES decrypt middle round from `Zvkned`.

## Important APIs, Types, And Functions
The consumed encoding is `1010001-----00000010-----1110111`, with variables `vs2` 24-20 and `vd` 11-7. The descriptor is non-privileged under the generator because U/VU access is not `never`.

## Control Flow, State, Dependencies, Risks, And Tests
The generation path walks, unmarshals, validates, builds, and serializes this descriptor into an `Insn` literal. Runtime decode scans the generated templates and extracts the two operands with `extractBits`. There is no state in the YAML itself. Risks include overlap with neighboring AES descriptors, loss of timing and extension metadata, and no operation semantics for deeper validation. Tests should verify table presence, correct opcode/mask values, decode separation from decrypt-final/encrypt-middle entries, and stable operand extraction.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdm.vv.yaml -->
