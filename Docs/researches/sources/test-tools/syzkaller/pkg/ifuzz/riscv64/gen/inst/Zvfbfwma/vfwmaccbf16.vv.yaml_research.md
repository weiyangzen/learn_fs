<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfwma/vfwmaccbf16.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfwma/vfwmaccbf16.vv.yaml

## Purpose
`vfwmaccbf16.vv.yaml` describes the vector-vector BF16 widening fused multiply-accumulate instruction from `Zvfbfwma`. It is the all-vector companion of the `.vf` descriptor.

## Important APIs, Types, And Functions
The generator reads match `111011-----------001-----1010111` and variables `vm`, `vs2`, `vs1`, and `vd`. Assembly is `vd, vs1, vs2, vm`; the variable list orders `vs2` before `vs1` according to encoding position, which is the order persisted into `Insn.Fields`.

## Control Flow, State, Dependencies, Risks, And Tests
The descriptor is converted by `buildInsn` into a static generated `Insn`. There is no state beyond generated Go source and init-time registration into `iset.Arches`. Dependencies are unified-db YAML, `yaml.v3`, `serializer`, and the RISC-V runtime descriptor types. Risks include operand-order confusion between assembly order and bitfield order, ignored BF16 arithmetic semantics, and no generated randomization of operands beyond the fixed opcode template. Tests should verify field order, opcode distinction from `.vf`, non-privileged registration, and decode results for encodings with varied `vm`, `vs2`, `vs1`, and `vd`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfwma/vfwmaccbf16.vv.yaml -->
