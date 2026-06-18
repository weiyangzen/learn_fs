# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gzspotan.h

Declares the spot analyzer device, trapezoid topology structures, and stem-generation API.

Key points:
- Describes the device as analyzing trapezoid-fill output for glyph grid fitting and antialiased rendering support.
- `gx_san_trap` stores geometry, outline boundary segment pointers, directions, topology contacts, band-list links, and stem-recognition flags.
- `gx_san_trap_contact` represents neighbor relationships across band boundaries as cyclic lists.
- `gx_san_sect` is the output stem/hint section with endpoints, outline segment pointers, and side mask.
- `gx_device_spot_analyzer` embeds a device plus lock count, trapezoid/contact buffers and freelists, topology reconstruction state, and global x extents.
- Provides GC descriptor macros with restricted pointer tracing assumptions.
- Declares obtain/release, begin, trapezoid storage, end, and stem generation functions.

Research notes:
- This is a private graphics helper rather than a display device.
- The API is callback-driven for extracted stem sections.
