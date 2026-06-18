# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jccoefct.c

Compressor coefficient buffer controller between forward DCT/quantization and entropy encoding.

Key points:
- Defines `my_coef_controller`, tracking iMCU row state, MCU position within row, a per-MCU block pointer buffer, and optional full-image virtual coefficient arrays.
- Supports pass-through single-pass mode and, when enabled, full coefficient buffering for Huffman optimization or multiscans.
- `start_iMCU_row` computes how many MCU rows belong to the current iMCU row, including partial bottom rows for noninterleaved scans.
- `compress_data` performs forward DCT for one iMCU row in single-pass mode, fills right/bottom dummy blocks with zero AC coefficients and repeated DC coefficients, and sends each MCU to entropy encoding.
- `compress_first_pass` DCTs all image components into virtual block arrays, pads right/bottom dummy blocks in the arrays, then calls `compress_output` to emit the current scan.
- `compress_output` reads DCT block pointers from virtual arrays for the active scan and sends MCUs to the entropy encoder.
- `jinit_c_coef_controller` allocates either a single MCU workspace or padded full-image virtual arrays per component.

Dependencies and interactions:
- Calls `fdct->forward_DCT`, `entropy->encode_mcu`, and memory-manager virtual block array APIs.
- Used by `jcmainct.c` in normal compression, directly by raw-data input, and by master-driven additional passes.

Risk notes:
- Suspension in single-pass mode causes the current MCU to be re-DCTed on retry.
- Full coefficient buffering only exists when entropy optimization or multiscans are compiled in.
- Dummy block generation assumes `blkn-1` is valid when copying DC values at bottom/right edges; this follows established MCU ordering assumptions.
