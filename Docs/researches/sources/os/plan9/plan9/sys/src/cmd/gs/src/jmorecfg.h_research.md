# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jmorecfg.h

## Identity

- Lines/bytes: 52 lines, 1,647 bytes.
- SHA-256: `1441dbd7262a998ee4034cdc09e9d50d805a288d4c5e03eb73b69e8953e76b99`.
- Role: active Ghostscript wrapper installed as IJG `jmorecfg.h`.
- Duplicate note: byte-identical to `jmorecf0.h`.

## Contents

The file includes `jmcorig.h`, then applies Ghostscript-specific feature reductions:

- Removes fast integer DCT.
- Removes floating DCT on systems without FPU support.
- Removes progressive/multiscan compression, entropy optimization, and input smoothing.
- Preserves progressive decompression for PDF 1.3 compatibility.
- Removes decoder smoothing, scaling, upsample merging, and color quantization features.
- Sets `D_MAX_BLOCKS_IN_MCU` to `64`.

## Dependencies

- Includes `jmcorig.h`.
- Uses `FPU_TYPE` from Ghostscript architecture configuration.

## Behavior And Integration

This is the filename IJG consumers include directly via `jpeglib.h`. In Ghostscript’s build flow, `jpeg.mak` creates/copies this wrapper so bundled IJG sources see Ghostscript’s reduced feature set.

## Research Notes

- This header determines which IJG source modules are useful in Ghostscript’s private build.
- It is a build/configuration artifact, not Plan 9 OS or filesystem logic.
