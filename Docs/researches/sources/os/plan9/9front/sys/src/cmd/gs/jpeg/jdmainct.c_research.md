# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdmainct.c

Main decompression buffer controller between coefficient output and postprocessing.

Key points:
- Holds downsampled component sample data in JPEG colorspace and feeds row groups to the postprocessor.
- Simple mode buffers one iMCU row, lets the coefficient controller fill it, and passes row groups through to upsampling/postprocessing.
- Context mode supports fancy vertical upsampling by creating two alternate "funny" pointer lists that preserve previous bottom row groups without copying data.
- Manufactures top and bottom context rows by pointer duplication, avoiding special cases in upsampling inner loops.
- Tracks context processing through `CTX_PREPARE_FOR_IMCU`, `CTX_PROCESS_IMCU`, and `CTX_POSTPONED_ROW`.
- Supports a crank-only path for the final pass of two-pass color quantization.
- Rejects full-image main buffering, since full buffering lives in coefficient or postprocessing controllers in this design.

Dependencies and interactions:
- Receives iMCU rows from `jdcoefct.c` and calls `jdpostct.c`.
- Context-row need is declared by `jdsample.c` when fancy 2h2v upsampling is selected.

Risk notes:
- Context rows are unsupported when `min_DCT_scaled_size < 2`.
- Bottom-of-image padding is delegated partly to the postprocessor/upsampler, so row counters must remain consistent.
- The pointer-list scheme is efficient but subtle; changes to row-group definitions can easily break it.
