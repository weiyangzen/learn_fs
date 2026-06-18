# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmr8n.c

RasterOp implementation for 8-bit gray and 24-bit RGB memory devices.

- Main entry point is `mem_gray8_rgb24_strip_copy_rop`.
- Handles 8-bit gray and 24-bit RGB destinations; comments note 16- and 32-bit cases fall back to the default implementation elsewhere.
- Detects constant source and texture, simplifies ROPs when constants equal device black or white, and records transparency sentinel values.
- For non-gray 8-bit devices, only simple cases are handled directly; complex cases fall back to `mem_default_strip_copy_rop`.
- Clips either as a copy or fill depending on whether source is constant.
- Uses macro-generated loops for 8-bit and 24-bit pixels, with cases split across constant/data source and constant/data texture.
- Supports 1-bit source/texture palettes and multi-bit source/texture data, including repeated strip textures with phase/shift.
- Risk notes: nested macro control flow is dense; transparency is implemented by skipping destination writes when source or texture equals the transparent sentinel.
