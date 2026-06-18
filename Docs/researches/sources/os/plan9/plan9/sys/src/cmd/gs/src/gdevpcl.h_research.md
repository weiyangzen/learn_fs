# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcl.h

This header exposes common definitions for PCL printer drivers.

It defines PCL paper-size numeric constants for Executive, Letter, Legal, Ledger, A0-A4, JIS B4/B5, Japanese postcards, Monarch, COM10, DL, C5, and B5. It declares `gdev_pcl_paper_size`, the helper that selects one of those codes from a Ghostscript device’s size and resolution.

It also declares 3-bit RGB printer color mapping procedures, `gdev_pcl_3bit_map_rgb_color` and `gdev_pcl_3bit_map_color_rgb`, and the row-compression entry points for PCL modes 2, 3, and 9. The header aliases `word` to `ulong` for mode 2 compression input.

The file depends on `gdevprn.h` for printer-device and Ghostscript type definitions.
