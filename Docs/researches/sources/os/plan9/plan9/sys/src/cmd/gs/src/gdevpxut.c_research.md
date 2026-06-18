# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxut.c

This file provides low-level PCL XL generation helpers used by the `gdevpx.c` driver.

High-level constructs:
- `px_write_file_header` writes the PJL prologue, selects grayscale or color render mode, enters PCL XL, writes session setup, writes device resolution, sets inch measure units, enables back-channel/error-page reporting, selects little-endian data organization, and opens the data source.
- `px_write_page_header` currently emits portrait orientation.
- `px_write_select_media` matches device width/height in inches against `px_enumerate_media` with a 5/72 inch tolerance, emits `MediaSize` and `MediaSource`, and returns the selected media code through `pms`.
- `px_write_file_trailer` emits `CloseDataSource`, `EndSession`, and PJL reset bytes. It takes `FILE *` because close/finalization may occur after stream teardown.

Low-level writers:
- `px_put_bytes` writes raw bytes to a Ghostscript stream.
- `px_put_a` and `px_put_ac` write attributes and attribute-plus-operator pairs.
- `px_put_ub`, `px_put_uba`, `px_put_us`, `px_put_usa`, and `px_put_u` emit compact unsigned values.
- `px_put_s`, `px_put_usp`, `px_put_usq_fixed`, `px_put_ss`, `px_put_ssp`, and `px_put_l` emit little-endian scalar, point, box, signed, and long values.
- `px_put_r` converts a floating-point value to single-precision IEEE-style bytes in little-endian order; `px_put_rl` adds the real32 tag.
- `px_put_data_length` chooses byte or long data-length tags.

The file centralizes the PCL XL endian assumption used by the driver: HP printers on this path only support little-endian data, so all numeric helpers emit low-byte-first operands.
