# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/siinterp.c

Image interpolation encode filter using DDA stepping and component scaling.

Key behavior:
- Defines `stream_IIEncode_state` with image scale parameters, input/output pixel sizes, row sizes, current row buffers, selected conversion case, and DDA state for X/Y mapping.
- `s_IIEncode_init` computes pixel sizes, initializes DDAs, allocates two row buffers, and selects an optimized scale/conversion case based on input/output bit depth, max values, and color count.
- `s_IIEncode_process` reads complete input rows into `cur`, maps output pixels to source X positions with DDA, converts component values between 8-bit and 16-bit representations, and writes output rows until the destination height is complete.
- `s_IIEncode_release` frees allocated row buffers.

Notable dependencies:
- DDA helpers: `gxdda.h`, `gxfixed.h`.
- Fraction conversion: `gxfrac.h`.
- Shared image scale params from `siinterp.h`/`sisparam.h`.

Research notes:
- The source allocates `prev` but the processing path only uses `cur`, so despite the filter name it behaves as a row/nearest mapping plus value conversion rather than full bilinear interpolation in this file.
- Comments mark allocation error returns as “WRONG” because they return `ERRC` instead of a VM error.
- A comment flags output-buffer handling as requiring an entire output pixel, so partial-pixel buffer edges are a known concern.
