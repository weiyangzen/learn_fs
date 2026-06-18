# File Research: sources/os/plan9/9front/sys/src/9/pc/nv_dma.h

Header of NVIDIA/XFree86-originated DMA register definitions for NV graphics acceleration. The file is primarily a collection of register offsets, field-position comments/macros, format values, and maximum transfer counts.

Content summary:
- Begins with NVIDIA copyright/license notice and XFree86 CVS provenance.
- Defines offsets and format values for objects such as:
  - `SURFACE_*`
  - `ROP_SET`
  - `PATTERN_*`
  - `CLIP_*`
  - `LINE_*`
  - `BLIT_*`
  - `RECT_*`
  - `RECT_EXPAND_*`
  - `STRETCH_BLIT_*`
- Many field names use a `31:16`/`15:0` notation as descriptive register bit ranges, not C expressions suitable for standalone use.
- Intended consumers are NVIDIA display acceleration code that writes command/data words to the GPU command interface.

Research notes:
- This is vendored hardware definition material rather than native Plan 9 logic.
- It has no functions or state; its significance is as a hardware contract for graphics code.
- The license notice requires retaining NVIDIA attribution in user documentation and internal comments when used.
