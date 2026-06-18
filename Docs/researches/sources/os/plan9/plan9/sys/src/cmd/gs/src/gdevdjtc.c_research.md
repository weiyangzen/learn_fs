# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdjtc.c

Implements the HP DeskJet 500C color printer device.

The device `gs_djet500c_device` is a 300 dpi, 3-bit RGB PCL printer using `gdev_pcl_3bit_map_rgb_color` and `gdev_pcl_3bit_map_color_rgb`. Compile-time defaults control shingling and depletion.

`djet500c_print_page` sends printer reset/setup commands, configures RGB raster mode, depletion, shingling, cursor position, and mode 2 compression. For each scan line it reads packed 3-bit RGB pixels, trims trailing zeros, transposes bytes into separate R, G, and B one-bit planes, skips blank lines, compresses each plane, and writes PCL raster-transfer commands in R/G/B order.

`mode2compress` is a local PackBits-style PCL mode 2 compressor supporting literal and repeated byte runs up to 127 bytes.

Dependencies are Ghostscript printer/PCL helpers plus direct `malloc`/`free`.

Risks: allocations use C library `malloc` rather than Ghostscript memory management. The print routine returns success even if allocation of plane buffers fails later would be problematic; it assumes allocations succeed after size checks. It is tuned for 300 dpi DeskJet 500C behavior and PCL mode 2.
