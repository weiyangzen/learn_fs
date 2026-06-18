# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevl31s.c

Implements the `lj3100sw` printer device for HP LaserJet 3100 Software output. It targets workflows where Ghostscript emits a spool format consumed by installed HP LaserJet 3100 software, including SMB printing through a Windows host.

The device uses `gdev_prn` printer infrastructure, media selection from `gdevmeds`, and custom section records. Main routines are `lj3100sw_print_page_copies`, `lj3100sw_close`, and helpers for section headers, buffered data emission, newline markers, and empty-line markers.

Raster output is monochrome run-length-like bit coding. The `code[2][65]` tables encode white and black pixel runs of up to 64 pixels, with special handling for all-white lines. High resolution is inferred from `x_pixels_per_inch > 300`; media dimensions and printer width/height come from fixed tables.

`select_medium` chooses among supported names (`a4`, `letter`, `legal`, envelopes, etc.), and the selected index drives the device-specific job header. Page data is horizontally centered by comparing printer width and Ghostscript page width.

Copies are represented in closing trailer records, not by re-rendering page data. Risks are mostly protocol brittleness: constants and section types are hard-coded to the HP software format.
