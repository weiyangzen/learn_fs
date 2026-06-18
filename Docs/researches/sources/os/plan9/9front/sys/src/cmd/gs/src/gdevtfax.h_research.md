# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtfax.h

## Purpose
Small public header for the TIFF/Fax writer helper used by fax-capable Ghostscript devices.

## Main Contents
- Declares `gdev_fax_print_page_stripped`, which writes a fax page through a CCITT Fax encoder with a caller-specified rows-per-strip value.

## Dependencies
The declaration depends on `gx_device_printer`, `FILE`, and `stream_CFE_state` types provided by including code.

## Filesystem Relevance
No filesystem logic. It declares an image-output helper.
