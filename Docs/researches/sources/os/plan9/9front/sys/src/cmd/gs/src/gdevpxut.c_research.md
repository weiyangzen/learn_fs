# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxut.c

This file provides low-level PCL XL generation helpers.

High-level constructs:
- `px_write_file_header` writes the PJL prologue, sets render mode to grayscale or color, enters PCL XL, writes session setup, resolution, measure units, error reporting, binary low-byte-first data organization, and opens the data source.
- `px_write_page_header` currently emits portrait orientation.
- `px_write_select_media` matches device width/height in inches against `px_enumerate_media` with a 5/72 inch tolerance, emits `MediaSize` and `MediaSource`, and returns the selected media code.
- `px_write_file_trailer` emits `CloseDataSource`, `EndSession`, and PJL reset.

Low-level writers:
- `px_put_bytes` writes raw bytes.
- `px_put_a`, `px_put_ac` write attributes and attribute+operator combinations.
- `px_put_ub`, `px_put_uba`, `px_put_us`, `px_put_usa`, `px_put_u` emit compact unsigned values.
- `px_put_s`, `px_put_usp`, `px_put_usq_fixed`, `px_put_ss`, `px_put_ssp`, `px_put_l` emit little-endian scalar, point, box, signed, and long values.
- `px_put_r` converts a floating-point value to single-precision IEEE-style bytes in little-endian order; `px_put_rl` adds the real32 tag.
- `px_put_data_length` chooses byte or long data-length tag.

The file assumes HP PCL XL printers support little-endian data and centralizes that encoding assumption for the driver.
