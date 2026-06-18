# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevp2up.c

## Purpose

`gdevp2up.c` defines `pcx2up`, a Ghostscript printer device used for testing page objects by writing two saved rendered pages side by side into a PCX output stream.

## Main Device

The file defines `gx_device_2up`, which extends the generic printer device with `have_odd_page` and a `gx_saved_page odd_page`. The exported device instance is `gs_pcx2up_device`, using 72 DPI, default page dimensions, 8-bit SVGA-style PC color mapping from `gdevpccm`, and `pcx2up_print_page` as the page writer.

## Control Flow

`pcx2up_open` forces banding by temporarily setting `MaxBitmap` to zero and selecting a band width large enough for two pages plus spacing. It then opens the printer device and resets the odd-page latch.

`pcx2up_print_page` alternates behavior by page parity. The first page of a pair is saved with `gdev_prn_save_page`. The second page is also saved, then the code builds two `gx_placed_page` entries with horizontal offsets. It allocates a temporary printer device copied from the `pcx2up` template, substitutes the real `pcx256` open and print-page procedures, opens it against the same output file, and calls `gdev_prn_render_pages` to render both saved pages into one output page. It then closes the temporary device and clears the odd-page latch.

## Dependencies

The file depends on `gdevprn.h` printer/page-saving APIs, `gdevpccm.h` PC palette mapping, `gxclpage.h` saved/placed page support, and the external `gs_pcx256_device` from `gdevpcx.c`.

## Filesystem Relevance

It writes through Ghostscript printer-device `FILE *` output but implements no filesystem semantics.

## Risks and Notes

If the job has an odd number of pages, the final saved odd page is not emitted by this file's own logic unless higher-level device finalization flushes it differently. Temporary device allocation errors return VM errors, but some error paths after allocation/open may rely on caller cleanup rather than freeing every intermediate object.
