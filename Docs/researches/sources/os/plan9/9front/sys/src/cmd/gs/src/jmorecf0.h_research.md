# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jmorecf0.h

Ghostscript wrapper around the original IJG `jmorecfg.h` body. It includes `jmcorig.h`, then removes unneeded JPEG library features to reduce the local Ghostscript JPEG build and align it with Ghostscript's requirements.

Feature changes after including `jmcorig.h`:
- Undefines `DCT_IFAST_SUPPORTED`.
- Undefines `DCT_FLOAT_SUPPORTED` when `FPU_TYPE <= 0`.
- Undefines encoder multiscanner/progressive support, entropy optimization, and input smoothing.
- Keeps decoder multiscanner/progressive support because progressive JPEG is needed for PDF 1.3.
- Undefines block smoothing, IDCT scaling, upsample scaling, upsample merging, and both one-pass and two-pass color quantization.
- Defines `D_MAX_BLOCKS_IN_MCU` as `64` to read nonstandard Adobe-generated JPEG/DCT streams with more blocks per MCU than the default IJG limit.

The include guard is `gsjmorec_INCLUDED`. In this source snapshot, `jmorecf0.h` and `jmorecfg.h` are byte-identical.

Filesystem relevance: none directly. This is JPEG decoder/encoder feature trimming for Ghostscript.
