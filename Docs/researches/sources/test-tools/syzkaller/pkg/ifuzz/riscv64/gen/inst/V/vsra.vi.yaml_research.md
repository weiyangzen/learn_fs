# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsra.vi.yaml

## Purpose

`vsra.vi` defines a RISC-V V-extension shift instruction for the ifuzz instruction generator. The
file binds the assembler form `vd, vs2, imm, vm` to an opcode pattern, operand bit fields, access
policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsra.vi` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, imm, vm`.

The decoder key is `encoding.match: 101001-----------011-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `imm@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VI_VADD`, `VI_VRSUB`, `VI_VAND`, `VI_VOR`,
`VI_VXOR`, `VI_VSADDU`, `VI_VSADD`, `VI_VSLL`, `VI_VSRL`, `VI_VSRA`, and 2 more; this file selects
the label matching `vsra.vi` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_shift_amount`, `illegal_normal`, `init_masked_result`, `read_vmask`,
`read_vreg`, `signed_saturation`, `unsigned_saturation`, `write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include shift amount masking, arithmetic sign fill, and rounding increment
rules are width-dependent.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, shift amounts above
SEW, signed high-bit inputs, rounding increment cases.
