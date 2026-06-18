# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdljm.h

Defines the interface and feature matrix for the generic monochrome HP DeskJet/LaserJet PCL driver.

The header documents that “PCL printer” support is feature-based rather than uniform. It defines spacing modes (`PCL_NO_SPACING`, `PCL3_SPACING`, `PCL4_SPACING`, `PCL5_SPACING`), compression support (`PCL_MODE_2_COMPRESSION`, `PCL_MODE_3_COMPRESSION`), and device properties such as raster reset behavior, duplex, paper size setting, and hardware copies.

It then composes known feature sets for DeskJet, DeskJet 500, FS-600, LaserJet variants, HP 2563B, and OCE 9050. These constants are consumed by `gdevdjet.c`.

Exports are `dljet_mono_print_page` and `dljet_mono_print_page_copies`.

Risk is low in code terms, but incorrect feature flags directly produce invalid printer command sequences or inefficient output.
