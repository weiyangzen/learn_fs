# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jmorecf0.h

## Identity

- Lines/bytes: 52 lines, 1,647 bytes.
- SHA-256: `1441dbd7262a998ee4034cdc09e9d50d805a288d4c5e03eb73b69e8953e76b99`.
- Role: Ghostscript wrapper for IJG `jmorecfg.h`.
- Duplicate note: byte-identical to `jmorecfg.h`.

## Contents

The file includes `jmcorig.h`, then disables JPEG features Ghostscript does not want or need:

- Disables `DCT_IFAST_SUPPORTED`.
- Disables `DCT_FLOAT_SUPPORTED` when `FPU_TYPE <= 0`.
- Disables compression multi-scan/progressive support, entropy optimization, and input smoothing.
- Keeps decompression multi-scan/progressive support because progressive JPEG is required for PDF 1.3.
- Disables block smoothing, IDCT scaling, upsample scaling, upsample merging, and both color quantizers.
- Defines `D_MAX_BLOCKS_IN_MCU 64` for Adobe compatibility.

## Dependencies

- Includes `jmcorig.h`.
- Uses `FPU_TYPE`, expected from Ghostscript architecture configuration.

## Behavior And Integration

This is the private JPEG feature policy for Ghostscript’s bundled IJG build. It narrows encoder capability while preserving decoder support needed by PDF workflows and nonstandard Adobe-produced JPEGs.

## Research Notes

- The Adobe compatibility setting increases decompressor MCU block tolerance beyond the IJG default.
- No unique behavior versus `jmorecfg.h`; both files are identical copies in this tree.
