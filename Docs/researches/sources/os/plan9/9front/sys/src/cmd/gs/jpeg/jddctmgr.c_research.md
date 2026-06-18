# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jddctmgr.c

Inverse DCT manager for decompression output passes.

Key points:
- Allocates per-component multiplier tables large enough for any supported IDCT method and initializes them to zero.
- `start_pass` selects reduced-size IDCTs for scaled output or full-size IDCTs based on `cinfo->dct_method`.
- Builds method-specific dequantization multiplier tables from each component's latched quantization table.
- Skips rebuilding tables for unneeded components or when the existing table already matches the selected method.
- Leaves all-zero multiplier tables in buffered-image cases where output begins before a component's quant table has been seen.
- Supports slow integer, fast integer, and floating AA&N scaling when compiled.

Dependencies and interactions:
- Depends on quantization tables latched by `jdinput.c`.
- Supplies function pointers used by `jdcoefct.c` during coefficient-to-sample conversion.

Risk notes:
- Missing compiled DCT method support triggers `JERR_NOT_COMPILED`.
- Invalid per-component scaled sizes trigger `JERR_BAD_DCTSIZE`.
- Neutral gray fallback for unseen quant tables is intentional but can hide absent component data until later input arrives.
