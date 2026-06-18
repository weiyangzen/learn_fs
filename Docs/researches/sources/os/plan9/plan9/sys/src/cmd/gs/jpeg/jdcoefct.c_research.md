# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdcoefct.c

Decompression coefficient buffer controller.

Key behavior:
- Sits between entropy decoding and inverse DCT, and also forms the buffered-image/transcoding coefficient-array interface.
- In single-pass mode, allocates one MCU workspace, decodes each MCU, immediately applies IDCT for needed components, and emits one iMCU row.
- In multiscan/buffered mode, consumes entropy-decoded coefficients into full-image virtual block arrays and later decompresses output rows from those arrays.
- Maintains input-side MCU counters and output-side iMCU row progress separately.
- Supports suspension by saving MCU column and vertical offsets before returning `JPEG_SUSPENDED`.
- Optional progressive block smoothing estimates early AC coefficients from neighboring DC values when coefficients are not yet fully known.
- `jinit_d_coef_controller` allocates either full-image virtual coefficient arrays or a single-MCU buffer and installs consume/decompress callbacks.

Dependencies:
- Calls entropy decoder `decode_mcu`, inverse DCT methods, input controller pass finishing, memory manager virtual block arrays, and IJG block-copy/zero helpers.

Notable risks:
- Full-buffer mode requires `D_MULTISCAN_FILES_SUPPORTED`; otherwise a request for full buffering fails.
- Block smoothing depends on progressive support, quantization table availability, nonzero quantizers, and coefficient-bit tracking.
- The single-pass path requires entropy decoding and output IDCT to proceed in lockstep.
