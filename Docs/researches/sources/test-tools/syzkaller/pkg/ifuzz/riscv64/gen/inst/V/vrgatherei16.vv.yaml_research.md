# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrgatherei16.vv.yaml

## Purpose

`vrgatherei16.vv` defines a RISC-V V-extension vector gather instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, vs1, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vrgatherei16.vv` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vd, vs2, vs1, vm`.

The decoder key is `encoding.match: 001110-----------000-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `vs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VV_VADD`, `VV_VSUB`, `VV_VAND`, `VV_VOR`,
`VV_VXOR`, `VV_VSADDU`, `VV_VSADD`, `VV_VSSUBU`, `VV_VSSUB`, `VV_VSMUL`, and 11 more; this file
selects the label matching `vrgatherei16.vv` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_sew_pow`, `get_shift_amount`, `get_vlen_pow`, `illegal_normal`,
`init_masked_result`, `read_vmask`, `read_vreg`, `signed_saturation`, and 2 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. For slide/gather
forms, the active-lane expression either shifts element indices by an immediate or scalar amount,
reads a selected source index, returns zero for out-of-range indices, and checks illegal
source/destination overlap where the ISA forbids in-place operation.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet,
VLEN/VLMAX index calculation helpers. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include out-of-range indices must return zero and illegal overlap with `vd`
must be detected.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, in-range and out-of-
range indices, destination overlap rejection.
