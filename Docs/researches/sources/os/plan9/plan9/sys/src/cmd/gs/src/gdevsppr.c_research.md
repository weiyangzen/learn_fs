# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsppr.c

Purpose: Ghostscript driver for Sun SPARCprinter devices using the LPVI ioctl interface.

Key behavior:
- Defines `sparc`, a 400 dpi monochrome printer device.
- `sparc_open` chooses A4 vs letter-style margins from page height and opens the printer device.
- `sparc_print_page` obtains and sets LPVI page metadata, copies the whole rendered bitmap into memory, and writes it to the printer file descriptor.
- On partial/failed writes, polls `LPVIIOC_GETERR`.
- Treats warning errors as retryable after sleeping 5 seconds; fatal/interface errors abort.
- Maintains a global `warning` flag to print “OK” after recovery.

Important dependencies:
- Sun printer ioctls from `<unbdev/lpviio.h>`.
- Ghostscript printer buffer copy helpers.

Notable risks / findings:
- If write fails after `out_buf` allocation and an error path returns, the buffer is not freed.
- Uses a global warning state and blocking sleeps inside output.
