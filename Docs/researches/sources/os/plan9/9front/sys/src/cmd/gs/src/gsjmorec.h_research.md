# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsjmorec.h

Wrapper over IJG `jmorecfg.h` for Ghostscript JPEG feature selection.

Key behavior:
- Includes `jmcorig.h`, then disables optional or unwanted JPEG encoder/decoder features.
- Disables fast integer DCT and disables floating DCT when `FPU_TYPE <= 0`.
- Disables compressor multiscan/progressive support and entropy optimization.
- Keeps decoder multiscan/progressive support because progressive JPEG is required for PDF 1.3.
- Disables smoothing, IDCT scaling, upsample scaling/merging, and quantization passes.
- Sets `D_MAX_BLOCKS_IN_MCU` to `64` for Adobe compatibility.

Dependencies:
- Depends on IJG configuration symbols and Ghostscript `FPU_TYPE`.

Research notes:
- This header trades optional JPEG features for a smaller, controlled build while preserving PDF-required progressive decoding.
