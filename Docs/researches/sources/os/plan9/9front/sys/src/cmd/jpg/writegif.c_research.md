# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/writegif.c

GIF89a writer for libdraw `Image` and `Memimage` inputs. Public functions include `startgif`, `memstartgif`, `writegif`, `memwritegif`, `endgif`, and `memendgif`.

It writes logical screen descriptors, global color tables for Plan 9 palette/gray depths, optional NETSCAPE loop extensions, comments, graphic-control blocks for delay/transparency, image descriptors, and LZW-compressed image data.

Supported channels are `GREY1`, `GREY2`, `GREY4`, `GREY8`, and `CMAP8`. The LZW encoder manages GIF sub-block output and dictionary resets at 12-bit code size.
