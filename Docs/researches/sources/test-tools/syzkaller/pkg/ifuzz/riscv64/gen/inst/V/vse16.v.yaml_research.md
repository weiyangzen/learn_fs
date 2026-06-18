# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vse16.v.yaml

## Purpose

`vse16.v` defines a RISC-V V-extension unit-stride element store instruction for the ifuzz
generator. The YAML maps the assembler form `vs3, (xs1), vm` to its opcode fields and, where
present, delegates behavior to the shared Sail store helpers used by the vector model.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vse16.v` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 000000-00000-----101-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew_pow`,
`illegal_store`, `process_vsseg`.

## Control Flow

Execution derives EEW, EMUL, element count, and field count from the encoding and current vector
type, rejects illegal store layouts, then delegates the actual memory walk to a shared helper such
as `process_vsseg`, `process_vsm`, or an indexed-store routine. The helper is responsible for mask
handling, address formation, and the architectural store side effects.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet, shared
vector memory helpers for element, mask, indexed, or segment stores. The schema is consumed with
neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand
names, and helper assumptions must remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include EEW/EMUL/nfield legality, masked memory side effects, address
calculation, and precise traps are mostly hidden behind helper calls or absent in metadata-only
entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, masked-off lanes
causing no memory write, misaligned/page-crossing addresses, segment field-count and EEW variants.
