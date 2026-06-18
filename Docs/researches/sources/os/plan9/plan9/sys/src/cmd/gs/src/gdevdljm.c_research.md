# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdljm.c

Provides the generic monochrome HP DeskJet/LaserJet PCL page emitter used by `gdevdjet.c`.

`dljet_mono_print_page` is a one-copy wrapper. `dljet_mono_print_page_copies` allocates working rows, initializes the printer and page, sets paper size/duplex/copy count when supported, starts raster graphics, reads each printer scan line, skips blank lines, chooses cursor movement or blank raster rows, and writes compressed or raw raster data.

Compression logic selects PCL mode 3 vs mode 2 per nonblank row when both are available, accounting for the cost of switching modes. It uses `gdev_pcl_mode3compress`, `gdev_pcl_mode2compress`, and a previous-row seed buffer. Unsupported printer-copy hardware falls back to default software copy output.

Important inputs are `dots_per_inch`, feature bit flags from `gdevdljm.h`, and a model-specific page initialization string.

Risks: the routine assumes enough memory for four row buffers and uses many PCL side effects. Correct blank-line skipping depends on printer feature flags, especially mode 3 seed-row clearing and no-spacing variants.
