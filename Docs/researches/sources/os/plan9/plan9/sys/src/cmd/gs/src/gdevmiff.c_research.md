# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmiff.c

ImageMagick MIFF direct-color output driver.

- Defines the `miff24` printer device at 72 dpi, 24-bit RGB, using standard RGB map/decode procs.
- `miff24_print_page` writes a simple MIFF header: `id=ImageMagick`, `DirectClass`, columns, rows, and run-length compression.
- Allocates one raster line and reads rows with `gdev_prn_get_bits`.
- Encodes each run as RGB bytes followed by a repeat count byte, with a maximum run count of 255.
- Frees the line buffer after processing and returns the last Ghostscript row-read status.
- Risk notes: file write errors from `putc`/`fputs` are not checked; only source scan-line errors affect the returned code.
