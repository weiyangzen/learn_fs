# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jidctfst.c

Purpose: fast, less-accurate integer inverse DCT implementation.

Key routine:
- `jpeg_idct_ifast()` performs dequantization and inverse DCT for one 8x8 block.

Important behavior:
- Compiled only when `DCT_IFAST_SUPPORTED` is enabled.
- Uses the AA&N scaled algorithm with 8 fractional bits for constants.
- Descales immediately after multiplies for speed.
- Dequantizes through the component `IFAST_MULT_TYPE` table.
- Runs columns into an integer workspace, then emits rows to the output buffer.
- Uses all-zero AC column shortcuts and optional row zero tests controlled by `NO_ZERO_ROW_TEST`.
- Final samples are descaled by `PASS1_BITS + 3` and range-limited.

Precision notes:
- For 8-bit samples it favors speed by avoiding an extra dequantization shift.
- For 12-bit samples it preserves more scaling accuracy.
