<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfmin/vfwcvtbf16.f.f.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfmin/vfwcvtbf16.f.f.v.yaml

## Purpose
`vfwcvtbf16.f.f.v.yaml` describes the `Zvfbfmin` widening conversion from bfloat16 vector elements to wider floating-point elements. It is the widening counterpart to the BF16 narrowing descriptor.

## Important APIs, Types, And Functions
The generator consumes `name: vfwcvtbf16.f.f.v`, assembly `vd, vs2, vm`, fixed match `010010------01101001-----1010111`, and variables `vm`, `vs2`, and `vd`. Access is allowed for S/U/VS/VU, so the generated entry is non-privileged.

## Control Flow, State, Dependencies, Risks, And Tests
The file enters the RISC-V table through `WalkDir`, YAML unmarshalling, `buildInsn`, and serialization. No local state exists; generated Go is the durable output. It integrates with `generated/insns.go`, `riscv64.Register`, `ParseInsn`, and tests that decode registered RISC-V instructions. Risks are similar to other data descriptors: BF16 semantic details, floating-point status effects, and `data_independent_timing: false` are not represented in `Insn`. The fixed bits must stay distinct from the generic `vfwcvt.f.f.v`. Tests should assert generated presence, three-field layout, opcode separation from non-BF16 conversion descriptors, and decode stability across operand bit variations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfmin/vfwcvtbf16.f.f.v.yaml -->
