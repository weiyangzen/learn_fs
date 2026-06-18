# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevlbp8.c

Provides Canon LBP-8II (`lbp8`) and Canon LIPS III (`lips3`) monochrome printer devices at 300 DPI. Both devices share `can_print_page`, differing mainly in initialization and termination command strings.

The code emits printer control sequences directly, then sends non-empty scanline segments. It trims trailing zero bytes, skips leading zero bytes by updating the horizontal column position, and splits output around long zero runs to reduce data sent to the printer.

Important constants include `LINE_SIZE`, 300 DPI defaults, and static init/end byte sequences for LBP-8 and LIPS III. Device descriptors are `gs_lbp8_device` and `gs_lips3_device`.

The raster path uses `gdev_prn_copy_scan_lines`, masks unused bits past page width with `rmask`, and sends graphics transfer commands via `fprintf` plus binary `fwrite`.

The file is narrow and device-protocol-specific. It assumes one-bit raster data and depends on exact ESC/CSI/DCS behavior for these Canon printers.
