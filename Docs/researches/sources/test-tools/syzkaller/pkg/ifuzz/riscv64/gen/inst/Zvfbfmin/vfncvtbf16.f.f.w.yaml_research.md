<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfmin/vfncvtbf16.f.f.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfmin/vfncvtbf16.f.f.w.yaml

## Purpose
`vfncvtbf16.f.f.w.yaml` describes the `Zvfbfmin` narrowing conversion from wider floating-point vector elements to bfloat16. It gives ifuzz coverage for the BF16 vector conversion opcode.

## Important APIs, Types, And Functions
The descriptor has assembly `vd, vs2, vm`, match `010010------11101001-----1010111`, and variables `vm` at bit 25, `vs2` at bits 24-20, and `vd` at bits 11-7. Unlike the crypto integer descriptors, it marks `data_independent_timing: false`, although this is not emitted into generated Go.

## Control Flow, State, Dependencies, Risks, And Tests
Generation accepts the 32-bit match, converts fixed bits to `OpcodeMask`/`Opcode`, and writes an `Insn` with three fields. The source has no state; its persistent footprint is the generated descriptor and registration side effect. Dependencies include the riscv-unified-db schema and the RISC-V generator. Risks include ignored floating-point rounding/exception semantics, ignored timing metadata, and no semantic `operation()` content for future differential tests. Tests should verify the generated entry has mask `4228903039` shape for OPFVF unary-style encodings, includes only `vm`, `vs2`, and `vd`, and decodes representative BF16 narrowing opcodes without colliding with other `vfncvt.*` forms.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfmin/vfncvtbf16.f.f.w.yaml -->
