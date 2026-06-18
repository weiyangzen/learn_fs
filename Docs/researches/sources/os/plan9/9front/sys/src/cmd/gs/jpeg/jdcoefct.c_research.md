# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdcoefct.c

Decompression coefficient buffer controller between entropy decoding and inverse DCT output.

Key points:
- Tracks input-side MCU position, iMCU row position, optional full-image virtual coefficient arrays, and optional progressive block-smoothing latch state.
- In one-pass mode, allocates a single MCU buffer, decodes one iMCU row at a time, immediately applies per-component IDCT, skips unneeded components, and avoids right/bottom dummy blocks.
- In multi-scan or buffered-image mode, `consume_data` decodes MCUs into full-image virtual block arrays, while `decompress_data` later emits IDCT output from those arrays.
- Forces input consumption when output is about to overrun available coefficient data, allowing buffered progressive/multiscan output to proceed incrementally.
- Supports optional progressive block smoothing by estimating the first five AC coefficients from neighboring DC values when they are not yet fully known.
- `jinit_d_coef_controller` selects single-MCU or full-image buffering, requests padded virtual arrays, and adjusts access-window size for smoothing.

Dependencies and interactions:
- Calls entropy decoder `decode_mcu`, IDCT manager function pointers, input controller pass transitions, and memory manager virtual block APIs.
- Full-image coefficient arrays are also exposed to transcoding via `jpeg_read_coefficients`.

Risk notes:
- Single-pass suspension retries may leave partially assigned workspace coefficients, relying on caller zeroing before decode.
- Full buffering depends on `D_MULTISCAN_FILES_SUPPORTED`; otherwise multiscan/buffered operation fails at initialization.
- Block smoothing is progressive-only and requires available quant tables plus nonzero early quantizers to avoid invalid estimation.
