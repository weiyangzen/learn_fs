# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpcl.c

## Purpose

`gdevpcl.c` provides shared utility routines for Ghostscript PCL printer drivers: paper-size code selection, 3-bit RGB color mapping, and PCL raster compression modes.

## Paper Size Selection

`gdev_pcl_paper_size` computes requested width and height in inches from device pixels and resolution, then scans known PCL paper sizes. It selects the smallest paper whose width and height are at least the requested size, preferring closest width and using height as a tie-breaker. The paper-size constants are declared in `gdevpcl.h`.

## Color Mapping

`gdev_pcl_3bit_map_rgb_color` maps RGB to a 3-bit additive color value used by PaintJet/DeskJet-style separate planes, then XORs with 7 because the buffering routines assume 0 means white. `gdev_pcl_3bit_map_color_rgb` reverses that encoding into full Ghostscript color values.

## Compression Routines

`gdev_pcl_mode2compress_padded` implements PackBits-like mode 2 compression. It scans words to find repeated byte runs, encodes literal runs up to 127 bytes as `count-1`, encodes repeated runs as `257-count`, and optionally trims zero padding from row ends. `gdev_pcl_mode2compress` is the normal wrapper with padding trimming disabled.

`gdev_pcl_mode3compress` implements LaserJet III delta row compression against a mutable previous row. It skips unchanged runs, encodes up to eight changed bytes with offset command bytes, updates `previous`, and supports long offsets with extension bytes.

`gdev_pcl_mode9compress` implements DeskJet 2D compression against a previous row. It identifies changed spans, then emits either uncompressed dissimilar bytes or compressed repeated-byte runs with compact offset/count encodings and extension bytes for larger counts.

## Dependencies

The file depends on `gdevprn.h`, `gdevpcl.h`, and math support. It uses Ghostscript scalar types and byte/word aliases but no device instances.

## Filesystem Relevance

No filesystem behavior is present. The routines transform raster rows for printer streams.

## Risks and Notes

The compressors assume callers provide enough output buffer for documented worst cases and valid row boundaries. Mode 2 uses `word` scanning for speed and explicitly may miss short byte runs. Mode 3 mutates the previous-row buffer, whereas mode 9 treats it as const; callers must respect that difference.
