# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpcl.h

## Purpose

`gdevpcl.h` declares shared constants and helper APIs for PCL-based Ghostscript printer drivers.

## Contents

The header defines PCL paper-size numeric codes for common paper sizes including Executive, Letter, Legal, Ledger, A-series, JIS B-series, Japanese postcard sizes, and envelopes. It declares `gdev_pcl_paper_size(gx_device *)` for selecting one of those codes from a device size.

It declares 3-bit RGB printer color mapping procs `gdev_pcl_3bit_map_rgb_color` and `gdev_pcl_3bit_map_color_rgb`.

It defines `typedef ulong word` and declares the row compression functions `gdev_pcl_mode2compress`, `gdev_pcl_mode2compress_padded`, `gdev_pcl_mode3compress`, and `gdev_pcl_mode9compress`.

## Dependencies and Integration

The header requires `gdevprn.h` and Ghostscript device proc types. PCL printer device implementations include this header to share page-size and raster-compression logic.

## Filesystem Relevance

No filesystem functionality is present.

## Risks and Notes

The `word` typedef is part of the compression API, so callers must use compatible alignment and row sizing. The paper-size comments note historical HP documentation ambiguity around 11x17 ledger/tabloid codes.
