# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevmem.h

This header defines Ghostscript memory devices: in-memory bitmap-backed devices used for mono, mapped-color, RGB/CMYK, planar, alpha, and band-buffer rendering. It requires `gxdevice.h` and includes `gxrplane.h`.

The introductory documentation enumerates four storage ownership models: device-allocated bitmap plus line pointers, client-provided bitmap with allocated line pointers, allocated line pointers with later caller setup, and fully caller-managed bitmap/line pointers. It also explains GC tracing flags for foreign bits and foreign line-pointer storage.

`gx_device_memory` subclasses `gx_device_forward_common` and adds raster, base pointer, bitmap allocator, line-pointer allocator, foreign-storage flags, planar metadata, initial matrix, line pointer table, palette, cached packed-color values for 24/40/48/56/64-bit formats, alpha-buffer mapping state, and planar depth.

`mem_device_init_private` is the initializer fragment for memory-device-specific fields. The public structure descriptor accounts for the forwarding target plus memory-device pointers.

The API computes required storage (`gdev_mem_bits_size`, `gdev_mem_line_ptrs_size`, `gdev_mem_data_size`, `gdev_mem_bitmap_size`), derives maximum height from a buffer size (`gdev_mem_max_height`), calculates raster via `gx_device_raster`, selects prototype memory devices by bit depth, creates mono/general/alpha memory devices, opens partial scan-line sets for banding, sets scan-line pointers, controls monobit polarity, and tests whether a device is memory or alpha-buffering.

Filesystem relevance: indirect only. This is an in-memory raster device and band buffer abstraction, not persistent storage or filesystem page cache code.
