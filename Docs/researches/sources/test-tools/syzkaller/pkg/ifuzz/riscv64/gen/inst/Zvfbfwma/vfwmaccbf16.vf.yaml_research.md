<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfwma/vfwmaccbf16.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfwma/vfwmaccbf16.vf.yaml

## Purpose
`vfwmaccbf16.vf.yaml` describes the `Zvfbfwma` vector-scalar widening fused multiply-accumulate instruction using bfloat16 inputs. It introduces a floating scalar operand `fs1`.

## Important APIs, Types, And Functions
The descriptor declares assembly `vd, fs1, vs2, vm`, match `111011-----------101-----1010111`, and fields `vm` 25-25, `vs2` 24-20, `fs1` 19-15, and `vd` 11-7. Its access block makes the generated instruction non-privileged.

## Control Flow, State, Dependencies, Risks, And Tests
`gen.go` turns this descriptor into an `Insn` with a fixed mask/opcode and four operand fields. Runtime integration is via generated registration and template matching in `ParseInsn`; encoding emits the fixed representative opcode because generated descriptors have `Generator: nil`. The YAML carries no mutable state. Risks include lost floating-point accumulation semantics, rounding/status behavior, BF16 extension requirements, and the difference between scalar `fs1` and vector `vs1` variants. Tests should compare `.vf` against `.vv`, verify the `fs1` field name, and ensure parse/decode coverage for representative BF16 WMA encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfwma/vfwmaccbf16.vf.yaml -->
