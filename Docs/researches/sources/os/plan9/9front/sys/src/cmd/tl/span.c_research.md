# File Research: sources/os/plan9/9front/sys/src/cmd/tl/span.c

Read completely: 1262 lines, 21791 bytes.

This is the ARM/Thumb linker span and operand-classification pass for the Plan 9 `tl` linker. It assigns program counters, sizes instructions through `oplook`, resolves branch sizing, handles Thumb padding/alignment, emits literal pools, defines `etext`/`textsize`, and builds ARM optab ranges.

Key behavior:
- `span` walks `firstp`, calls `setarch`, sizes each `Prog`, updates text symbol values, flushes literal pools, and reruns passes when large branches or Thumb branch alignment change instruction sizes.
- `checkpool`, `flushpool`, and `addpool` manage PC-relative literal pools and insert branch-around-pool instructions.
- `aclass` classifies ARM operands, computes `instoffset`, resolves external/static/auto/param addressing, and diagnoses undefined externals.
- `oplook`, `cmp`, `ocmp`, and `buildop` build and search instruction encoding tables.
- `dynreloc` and `asmdyn` collect sorted dynamic relocation records and write import/relocation metadata.

Dependencies:
- Includes `l.h` and relies on linker globals such as `firstp`, `thumb`, `blitrl`, `elitrl`, `curtext`, `autosize`, symbol tables, `optab`, `oprange`, `thumboptab`, and output helpers.

Reliability notes:
- This file is central to link correctness: branch range, literal pool distance, and Thumb/ARM interworking calculations are stateful and order-sensitive.
- Several paths diagnose then continue by assigning default symbol types, which is normal for old Plan 9 toolchains but fragile for malformed inputs.
