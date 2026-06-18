# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jddctmgr.c

Purpose: inverse-DCT manager for decompression.

Key structures and routines:
- `my_idct_controller` extends `jpeg_inverse_dct` and tracks the current IDCT method per component.
- `multiplier_table` union reserves enough storage for slow integer, fast integer, and float multiplier tables.
- `start_pass()` chooses the IDCT implementation per component and builds the dequantization multiplier table.
- `jinit_inverse_dct()` allocates the controller and per-component multiplier tables.

Important behavior:
- Handles reduced-size IDCTs when `IDCT_SCALING_SUPPORTED` is compiled in: 1x1, 2x2, and 4x4 use ISLOW-style multiplier tables.
- Full-size IDCT selection follows `cinfo->dct_method`: `JDCT_ISLOW`, `JDCT_IFAST`, or `JDCT_FLOAT`, depending on compile-time support.
- Skips table rebuilds when the component is not needed or the table already matches the active method.
- If a component has not yet latched a quantization table in buffered-image mode, its multiplier table remains zeroed, producing neutral output.

Dependencies:
- Uses quant tables saved in `jpeg_component_info.quant_table`.
- Calls IDCT routines declared in `jdct.h`.
- Relies on JPEG memory manager and compile-time feature macros.

Notes:
- No per-block IDCT work happens here; this file only performs pass setup and table preparation.
