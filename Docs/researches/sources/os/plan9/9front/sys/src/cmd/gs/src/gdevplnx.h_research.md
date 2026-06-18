# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevplnx.h

Public header for the Ghostscript plane extraction device.

Key contents:
- Includes `gxrplane.h` for `gx_render_plane_t`.
- Documents the plane extraction model: the client sees a color-capable forwarding device, while a selected group of bits is rendered into a separate plane device.
- Defines `gx_device_plane_extract`, embedding `gx_device_forward_common`, the destination `plane_dev`, selected `plane`, derived plane white/mask information, memory-device detection, and dynamic `any_marks` state.
- Declares the GC structure descriptor `st_device_plane_extract` and `public_st_device_plane_extract()`.
- Declares `plane_device_init()` for initializing a plane extraction device around a target, plane device, selected plane, and optional clear operation.

Notable dependencies:
- Requires Ghostscript forwarding-device definitions from the including context and `gx_render_plane_t` from `gxrplane.h`.

Research notes:
- The header states important limits: target and extraction device depths are limited to 32 bits, and each plane is limited to 8 bits.
- The original use case is band-list rendering for plane-oriented color printers.
