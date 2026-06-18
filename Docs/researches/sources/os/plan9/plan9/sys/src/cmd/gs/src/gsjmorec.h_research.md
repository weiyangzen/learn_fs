# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsjmorec.h

Wrapper around IJG `jmorecfg.h` via `jmcorig.h`, pruning JPEG encoder/decoder features not needed by this Ghostscript build. It disables fast integer DCT, optional floating DCT when no FPU is available, multiscanning/progressive encoding, entropy optimization, input smoothing, block smoothing, IDCT scaling, upsample scaling/merging, and quantization passes.

Progressive and multiscanning decode support is intentionally retained because progressive JPEG is required for PDF 1.3. It raises `D_MAX_BLOCKS_IN_MCU` to 64 for Adobe compatibility on unusual JPEG files.

This file is compile-time feature selection for embedded IJG code.
