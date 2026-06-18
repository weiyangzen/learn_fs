# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxrplane.h

Planar rendering helper declarations for extracting one plane from chunky pixels.

Key contents:
- Forward-declares `gx_device`.
- Defines `gx_render_plane_t` with bit depth, least-significant-bit shift, and plane/screen index.
- Declares `gx_render_plane_init`, which initializes a plane specification for a given device and plane index.

Notable dependencies:
- Device-specific color layout is supplied by the implementation/device, not by this header.

Research notes:
- The header says the structure should be treated as opaque by callers despite its fields being visible.
- Comments note that plane selection is currently fixed-procedure based but should eventually become a device/color-info property.
