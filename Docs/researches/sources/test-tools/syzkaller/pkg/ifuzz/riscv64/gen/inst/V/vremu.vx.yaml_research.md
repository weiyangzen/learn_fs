# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vremu.vx.yaml

## Purpose

`vremu.vx` defines a RISC-V V-extension remainder instruction for the ifuzz instruction generator.
The file binds the assembler form `vd, vs2, xs1, vm` to an opcode pattern, operand bit fields,
access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vremu.vx` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, xs1, vm`.

The decoder key is `encoding.match: 100010-----------110-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `MVX_VAADDU`, `MVX_VAADD`, `MVX_VASUBU`,
`MVX_VASUB`, `MVX_VSLIDE1UP`, `MVX_VSLIDE1DOWN`, `MVX_VMUL`, `MVX_VMULH`, `MVX_VMULHU`,
`MVX_VMULHSU`, and 4 more; this file selects the label matching `vremu.vx` through the fixed
encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_scalar`, `get_sew`, `illegal_normal`, `init_masked_result`, `read_vmask`,
`read_vreg`, `write_vreg`.

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

Risks and edge cases include division-by-zero and signed overflow remainder cases must match the
ISA's special return values.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, zero divisor, unsigned
and signed operands, minimum signed value divided by -1.
