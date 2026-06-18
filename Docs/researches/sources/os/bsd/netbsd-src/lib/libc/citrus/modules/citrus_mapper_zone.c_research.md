# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_zone.c

## Scope

Implements the Citrus `mapper_zone` mapper module. It maps integer code indices only when they fall inside configured row/column zones, optionally applying row and column offsets.

## APIs And Behavior

- Exports mapper operations through `_citrus_mapper_zone_mapper_getops()`.
- Parses mapper variables in either single-column form or `rowzone/colzone/bits` form.
- Accepts offset specifications after `:`, with signed row/column offsets.
- `_citrus_mapper_zone_mapper_convert()` splits source indices by `mz_col_bits`, validates row/column membership, applies offsets, and returns either success or `_CITRUS_MAPPER_CONVERT_NONIDENTICAL`.
- Declares itself stateless with one source and one destination index per conversion.

## Dependencies

Uses Citrus mapper/module interfaces, `_memstream`, `_region`, basic character helpers, and mapper traits.

## Risks And Invariants

- Zone ranges and offsets are bounds-checked so offset application does not cross the configured row/column bit width.
- `mz_col_bits` controls both source splitting and destination packing, so bit-width parsing errors would corrupt mappings.
- The module allocates `cm->cm_closure`; uninit is empty, so lifetime depends on the surrounding mapper framework behavior.
