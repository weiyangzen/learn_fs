<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbb/vwsll.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbb/vwsll.vv.yaml

## Purpose
`vwsll.vv.yaml` is a riscv-unified-db instruction descriptor for the `Zvbb` vector bit-manipulation instruction `vwsll.vv`. It describes the vector-vector widening shift-left logical form with assembly operands `vd, vs2, vs1, vm`.

## Important APIs, Types, And Functions
The file is declarative input for `pkg/ifuzz/riscv64/gen/gen.go`. The consumed API surface is `kind: instruction`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. Its 32-bit match string is `110101-----------000-----1010111`; variable fields are `vm` bit 25, `vs2` bits 24-20, `vs1` bits 19-15, and `vd` bits 11-7.

## Control Flow, State, Dependencies, Risks, And Tests
Generation discovers the YAML through `filepath.WalkDir`, unmarshals it with `gopkg.in/yaml.v3`, converts the fixed bits into an opcode/mask, and emits one `riscv64.Insn` if the match has exactly 32 characters and all locations parse as `hi-lo` ranges. The descriptor has no runtime state; its persisted effect is one generated table entry with `AsUInt32` equal to the opcode and `Priv` false because U/VU access is allowed. It integrates with `riscv64.Register`, `ParseInsn`, and generic ifuzz tests through the generated package import. Risks are mostly schema loss: extension gating, `data_independent_timing: true`, and the empty `operation()` block are not preserved by the generator. Test signals should assert generated presence, field order, mask/opcode matching, and decode round trips for randomized variable fields.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbb/vwsll.vv.yaml -->
