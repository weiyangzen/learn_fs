# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevlp8k.c

Implements the `lp8000` Epson LP-8000 ESC/Page monochrome laser printer driver at 300 dpi.

Key behavior:
- Registers `gs_lp8000_device` with fixed margins and `lp8000_print_page`.
- Writes a large ESC/Page/EJL initialization sequence before raster output.
- Computes printer coordinates with a 60-pixel offset, then aligns the left margin to a byte boundary.
- Scans from top margin to bottom margin, skipping consecutive blank lines.
- For nonblank lines, trims leading and trailing zero bytes.
- Compresses remaining bytes using the LP-8000 repeated-byte format: two repeated bytes followed by an insertion count, splitting runs longer than 257 bytes.
- Emits X coordinate updates only when the trimmed left edge changes.
- Emits Y coordinate, compressed byte count, point count, bitmap mode command, and compressed data for each line.
- Writes a termination and reinitialization sequence at end of page.

Dependencies and notes:
- Uses `gdev_prn_get_bits` for blank-line detection and `gdev_prn_copy_scan_lines` for actual line copy.
- The long file comment documents the reverse-engineered LP-8000 protocol and its compressed data format.
- Handles only the 300x300 dpi mode described by the constants and init strings.
