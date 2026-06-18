# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsbc.vvm.yaml

## Purpose

`vsbc.vvm` defines a RISC-V V-extension subtract-with-borrow instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, vs1, v0` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsbc.vvm` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, vs1, v0`.

The decoder key is `encoding.match: 0100100----------000-----1010111` with variables `vs2@24-20`,
`vs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VVMS_VADC`, `VVMS_VSBC`; this file selects
the label matching `vsbc.vvm` through the fixed encoding pattern.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew`,
`illegal_vd_masked`, `init_masked_result`, `read_vmask_carry`, `read_vreg`, `write_vreg`.

## Control Flow

Execution uses the carry-mask path rather than normal element masking: it rejects masked
destination-register overlap with `illegal_vd_masked`, reads borrow bits from `v0` through
`read_vmask_carry`, initializes all lanes as active, subtracts `vs1` and the borrow bit from `vs2`,
writes `vd`, and clears `vstart`.

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

Risks and edge cases include borrow bits are read from `v0`, not the normal mask path, and
destination-mask overlap is illegal.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, borrow mask lanes from
v0, vd mask-register overlap rejection.
