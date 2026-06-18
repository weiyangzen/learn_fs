# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdljm.h

Interface and feature-flag header for the generic monochrome HP DeskJet/LaserJet PCL driver.

Key contents:
- Defines vertical-spacing capability flags: `PCL_NO_SPACING`, `PCL3_SPACING`, `PCL4_SPACING`, `PCL5_SPACING`, and `PCL_ANY_SPACING`.
- Defines printer capabilities: mode 2/mode 3 compression, raster-end reset behavior, duplex, paper-size selection, and copy-count commands.
- Provides shorthand feature combinations such as `PCL_MODE0`, `PCL_MODE2`, `PCL_MODE3`, and no-spacing variants.
- Defines known feature masks for DeskJet, DeskJet 500, FS-600, LaserJet variants, LP2563B, and OCE9050.
- Declares `dljet_mono_print_page` and `dljet_mono_print_page_copies`.

Notable dependencies:
- Includes `gdevpcl.h` for PCL-related constants and helper declarations.

Research notes:
- The header explicitly warns that “PCL printer” is an approximation; feature flags encode model-specific command subsets.
- It is tightly paired with `gdevdljm.c` and consumed by model wrappers in `gdevdjet.c`.
