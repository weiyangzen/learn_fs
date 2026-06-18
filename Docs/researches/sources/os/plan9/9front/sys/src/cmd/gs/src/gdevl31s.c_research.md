# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevl31s.c

Implements the `lj3100sw` printer device for HP LaserJet 3100 Software. It emits the proprietary stream expected by installed LaserJet 3100 software, with media selection support from `gdevmeds.c`.

Key behavior:
- Defines supported media names and printer dimensions for 300 dpi and high-resolution modes.
- Registers `gs_lj3100sw_device` via a printer device descriptor with custom `lj3100sw_print_page_copies` and `lj3100sw_close`.
- Uses `select_medium(pdev, media, LARGEST_MEDIUM)` to choose a medium that fits the rendered image.
- Encodes raster lines using two static variable-length code tables for white and black run lengths from 0 to 64 pixels.
- Buffers output in `BUFFERSIZE` chunks, emitting section headers with little-endian 16-bit fields.
- On a new printer file, writes job setup records including resolution, selected medium, printer width, and control fields.
- Centers page data horizontally inside the selected printer width.
- Handles all-white lines through compact empty-line byte sequences that differ by resolution.
- On close, writes termination sections and then delegates to `gdev_prn_close`.

Dependencies and notes:
- Relies on `gdevprn.h` and `gdevmeds.h`.
- `num_copies` argument is ignored; the driver uses `ppdev->NumCopies`.
- The run-length codec is local to this driver and tightly coupled to the LaserJet 3100 software protocol.
