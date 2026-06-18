# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevp2up.c

This file implements `pcx2up`, a test Ghostscript printer device that saves two rendered pages and emits them side-by-side into one PCX output page. It is a graphics/printer-device utility, not a filesystem implementation.

The device extends the generic printer structure with `have_odd_page` and `odd_page`. `pcx2up_open` temporarily changes printer space parameters to force banding and delayed rasterization. It sets a band width large enough for two pages plus spacing, caps band buffer space with `RENDER_BUFFER_SPACE`, calls `gdev_prn_open`, restores the caller-visible space parameters, and clears the odd-page flag.

`pcx2up_print_page` alternates behavior by page parity. On the first page, it saves the rendered page into `odd_page` with `gdev_prn_save_page`. On the second page, it saves the even page, builds two `gx_placed_page` descriptors with horizontal offsets, allocates a temporary printer device cloned from `gs_pcx2up_device`, swaps in the open and print procedures from `gs_pcx256_device`, opens the temporary render device, and calls `gdev_prn_render_pages` to paint both saved pages into the final PCX stream.

Important details: output is hardwired around the `pcx256` backend, the device forces banding to preserve pages for later placement, and cleanup avoids closing the original output file by clearing `prdev->file` before closing the temporary device.
