# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jidctfst.c

Fast, less-accurate integer inverse DCT implementation, compiled under `DCT_IFAST_SUPPORTED`. It uses the AA&N scaled algorithm with only 8 fractional bits for constants and immediate descaling after multiplies.

The exported `jpeg_idct_ifast()` performs dequantization through the component `IFAST_MULT_TYPE` table, runs columns into an integer workspace, then emits rows to the output buffer. For 8-bit samples it favors speed by avoiding an extra dequantization shift; for 12-bit samples it preserves more scaling accuracy.

The code includes column all-zero AC shortcuts and an optional row zero test controlled by `NO_ZERO_ROW_TEST`. Final samples are descaled by `PASS1_BITS + 3` and range-limited.
