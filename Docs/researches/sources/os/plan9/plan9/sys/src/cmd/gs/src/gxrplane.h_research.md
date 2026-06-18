# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxrplane.h

`gxrplane.h` declares planar rendering support. It forward-declares `gx_device`.

`gx_render_plane_t` describes extraction of one plane from chunky pixels. It contains `depth`, bit `shift` of the least significant bit from the low end, and an `index` within a multi-screen halftone. The comment says callers should treat this structure as opaque and initialize it only through the provided procedure.

`gx_render_plane_init` initializes a plane specification for a device and plane index. The device decides which bits constitute the plane; the comment notes this is currently fixed-procedure behavior but may eventually be moved into device properties or `color_info`.

The file is a compact interface layer for code that renders or separates individual planes from packed device pixels.
