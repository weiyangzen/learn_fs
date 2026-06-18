# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcl.c

This file provides shared utility routines for PCL-based Ghostscript printer drivers.

`gdev_pcl_paper_size` computes a PCL paper-size code from the device width, height, and resolution. It chooses the smallest standard size whose width and height are at least the requested page size, prioritizing close width matches because many printers center paper in the tray. It supports Executive, Letter, Legal, Ledger, A-series, JIS B sizes, Japanese postcards, Monarch, COM10, DL, C5, and B5.

The color helpers implement a 3-bit RGB plane model used by PaintJet/DeskJet-style devices. `gdev_pcl_3bit_map_rgb_color` takes the high bit of each RGB component, packs R/G/B into three bits, and complements the result because the buffering convention uses zero as white. `gdev_pcl_3bit_map_color_rgb` reverses this encoding.

The compression helpers implement multiple PCL raster compression modes. `gdev_pcl_mode2compress_padded` and `gdev_pcl_mode2compress` implement PackBits-like run/literal compression for DeskJet/LaserJet IIp output, with an optional padding behavior that preserves trailing zeros. `gdev_pcl_mode3compress` implements LaserJet III delta compression by comparing the current row to a mutable previous row and emitting changed spans with offsets. `gdev_pcl_mode9compress` implements a 2D DeskJet compression mode using unchanged-row skips, uncompressed dissimilar spans, and run-length encoded similar spans. These functions operate at byte/word row level and return compressed byte counts.
