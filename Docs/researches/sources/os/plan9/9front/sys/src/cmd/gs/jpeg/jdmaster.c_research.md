# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdmaster.c

Master controller for decompression module selection, output dimensions, and pass orchestration.

Key points:
- `jpeg_calc_output_dimensions` computes 1/1, 1/2, 1/4, or 1/8 output scaling, chooses per-component IDCT scaled sizes, recomputes downsampled dimensions, and sets output component counts.
- `use_merged_upsample` gates the optimized merged path to non-fancy, non-CCIR, YCbCr-to-RGB, 2h1v/2h2v, unscaled component cases.
- `prepare_range_limit_table` builds the shared sample clamp/wrap table used by IDCT and color conversion.
- `master_selection` initializes color quantizers, color conversion/upsampling/postprocessing, inverse DCT, entropy decoder, coefficient controller, and main controller.
- Selects progressive versus sequential Huffman decoders; arithmetic coding is reported as not implemented.
- Chooses full coefficient buffering when input has multiple scans or buffered-image mode is enabled.
- Initializes virtual arrays, starts the first input pass, and sets progress accounting for multiscan input.
- `prepare_for_output_pass` chooses dummy versus real output passes, switches between one-pass/two-pass quantizers, and starts all active modules in pass order.
- `finish_output_pass` finishes quantizer work and advances pass count.
- `jpeg_new_colormap` supports switching external colormaps between buffered-image output passes when two-pass quantization is active.

Dependencies and interactions:
- Central integration point for `jdinput.c`, `jdcoefct.c`, `jddctmgr.c`, `jdhuff.c`/`jdphuff.c`, `jdcolor.c`, `jdsample.c`, `jdmerge.c`, `jdpostct.c`, and color quantizers.

Risk notes:
- Several options depend on compile-time feature macros; missing modules produce `JERR_NOT_COMPILED`.
- Quantization is incompatible with raw-data output.
- Merged upsampling constraints must remain synchronized with `jdmerge.c` capabilities.
