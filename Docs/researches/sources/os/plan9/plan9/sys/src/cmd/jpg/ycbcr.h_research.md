# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/ycbcr.h

This header is a data table module for Plan 9 JPEG/YUV color conversion. It defines `uint ycbcrmap[256]`, a 256-entry packed color lookup table, and `uchar closestycbcr[16*16*16]`, a 4096-entry quantization/nearest-color lookup table.

The file has no functions, includes, guards, or declarations beyond table definitions. It is intended to be included by exactly one C translation unit, not shared as an extern-only interface.

Key behavior is lookup-driven conversion between indexed/quantized RGB-like values and YCbCr palette entries. The final blocks of `closestycbcr` map high quantized ranges heavily to entries `254` and `255`, indicating reserved or extreme palette values.

Risks and notes: because this header defines storage directly, including it from more than one object would create duplicate symbols. Its correctness is entirely data-dependent and hard to audit mechanically without a generator or reference palette.
