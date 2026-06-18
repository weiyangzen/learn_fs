# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/writerawimage.c

Writer for Plan 9 compressed image format from `Rawimage`. It emits a `compressed` header with channel descriptor and rectangle, then compresses scanline blocks.

Supported `Rawimage` descriptors include `CY`, `CYA16`, `CRGBV`, `CRGBVA16`, `CRGB24`, and `CRGBA32`, mapped to draw channel descriptors such as `GREY8`, `CMAP8`, `RGB24`, and `RGBA32`.

The compressor uses Plan 9 image compression constants (`NMATCH`, `NRUN`, `NDUMP`, `NMEM`) and a hash-chain sliding window, flushing blocks when the encoded buffer fills.
