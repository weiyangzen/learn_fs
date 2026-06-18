# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsropt.h

## Purpose
Defines Ghostscript RasterOp and logical-operation types, constants, and Boolean transformation macros. It covers PCL/PostScript-facing 2-input and 3-input RasterOps, transparency flags, render-algorithm packing, and exported RasterOp execution/usage tables.

## Public Surface
- `gs_rop2_t`: 2-input RasterOp enum with source, destination, zero, one, and default source operation.
- `gs_rop3_t`: 3-input RasterOp enum using D, S, and T truth-table encodings.
- `gs_logical_operation_t`: packed integer containing low 8-bit ROP3 code, source/pattern transparency flags, render algorithm bits, and the `lop_pdf14` marker.
- `rop_operand`, `rop_proc`, `rop_usage_t`: operand word type, function-pointer type, and operand usage enum.
- `extern const rop_proc rop_proc_table[256]` and `extern const byte rop_usage_table[256]`.

## Macro Behavior
- ROP truth-table constants are arranged so Boolean C operators on constants produce corresponding ROP codes, provided results are masked appropriately.
- `rop3_invert_*`, `rop3_know_*`, `rop3_swap_S_T`, and `rop3_not` transform ROP truth tables.
- `rop3_use_D_when_*` folds source/texture transparency into a ROP by forcing destination preservation for transparent pixels.
- `rop3_uses_*` and `rop3_is_idempotent` provide compile-time/test macros for usage and idempotence.
- `lop_*` macros extract ROP bits, check S/T use, account for transparency, and handle PDF 1.4 transparency as non-idempotent through `lop_pdf14`.

## Dependencies
Requires Ghostscript base integer and byte typedefs from surrounding includes. It exports data implemented in `gsroptab.c`.

## Risks and Notes
- `TRANSPARENCY_PER_H_P` selects the HP-compatible interpretation where transparency flags can make `lop_uses_S` true even if the raw ROP does not use source. This is intentionally described as bizarre but necessary.
- The packed `gs_logical_operation_t` representation is performance-driven and depends on bit layout stability.
