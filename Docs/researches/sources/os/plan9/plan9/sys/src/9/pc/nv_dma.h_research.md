# File Research: sources/os/plan9/plan9/sys/src/9/pc/nv_dma.h

NVIDIA 2D DMA/register macro definitions imported from the XFree86 NV driver lineage.

Key elements:
- Contains NVIDIA copyright/license notice.
- Defines offsets and bit-field notation for surface format/pitch/offset, ROP, pattern, clipping, line drawing, blit, solid rectangle, mono/color expansion, and stretch blit objects.
- Includes max batch counts for line/rectangle/data command arrays.
- Encodes formats for 8/15/16/24-bit depths and YUYV/UYVY stretch blit formats.

Interactions:
- Header only; intended for NVIDIA VGA acceleration driver code in the same PC graphics subsystem.
- Uses unusual `FIELD 31:16` style macro names as documentation/constants for packed register fields.

Research notes:
- Graphics acceleration metadata only, not filesystem or storage logic.
