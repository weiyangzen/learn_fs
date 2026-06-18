# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdljm.c

Generic monochrome HP DeskJet/LaserJet PCL raster output engine shared by multiple printer-specific wrappers.

Key behavior:
- `dljet_mono_print_page` delegates to `dljet_mono_print_page_copies` with one copy.
- Allocates a shared work buffer for current input row, compressed output row, alternate compressed row, and previous seed row.
- Initializes printer state, paper size, duplex mode, per-page setup, copies, raster end/start, and resolution.
- Scans rendered rows, masks bits beyond page width, skips trailing zero words, tracks blank lines, and chooses whether to output blank rows or vertical-positioning commands.
- Supports PCL no-compression, mode 2 compression, and adaptive mode 2/mode 3 compression, including mode-switch penalty accounting.
- Maintains/clears the seed row required by mode 3 compression.
- Ends raster graphics, ejects the page, frees temporary storage, and returns the last copy/print error.

Notable dependencies:
- Ghostscript printer API: `gdevprn.h`.
- PCL helpers and feature flags from `gdevdljm.h`, including `gdev_pcl_mode2compress`, `gdev_pcl_mode3compress`, and paper-size helpers.

Research notes:
- This is the central implementation behind several printer devices in `gdevdjet.c`.
- It has many printer-behavior workarounds encoded through feature flags, especially around vertical spacing, seed-row clearing, duplex, copies, and paper-size commands.
- Temporary storage is manually partitioned in word-sized chunks for faster scanning and compression.
