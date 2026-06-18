# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg4ei8.v.yaml

## Purpose

`vsoxseg4ei8.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg4ei8.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 011011-----------000-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
