# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsext.vf8.yaml

## Purpose

`vsext.vf8` defines a RISC-V V-extension sign-extension instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, vm` to an opcode pattern, operand bit fields,
access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsext.vf8` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vd, vs2, vm`.

The decoder key is `encoding.match: 010010------00011010-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VEXT8_ZVF8`, `VEXT8_SVF8`; this file
selects the label matching `vsext.vf8` through the fixed encoding pattern.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew`,
`illegal_variable_width`, `init_masked_result`, `read_vmask`, `read_vreg`, `valid_reg_overlap`,
`write_vreg`.

## Control Flow

Execution reads a narrower source vector using the fractional width implied by the suffix, checks
variable-width legality and overlap, initializes masked results from the old destination, then zero-
or sign-extends each active source element into the current SEW before writing `vd`.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet,
variable-width legality and register-overlap helpers. The schema is consumed with neighboring
V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and
helper assumptions must remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include fractional LMUL, narrow source register grouping, and destination
overlap constraints are legality-sensitive.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, vf2/vf4/vf8 legality
across SEW, sign-bit propagation, register overlap failures.
