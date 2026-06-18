# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sddparam.c

Parameter get/put support for `DCTDecode`.

It provides:

- `s_DCTD_get_params`, which writes common DCT parameters. The code has an `NYI` comment and uses a default state for comparison.
- `s_DCTD_put_params`, which reads common DCT parameters and then accepts `HuffTables` and `QuantTables` for JPEG streams that omit those tables.

This file delegates most work to shared helpers in `sdcparam.c`.

It is JPEG/DCT filter parameter code, not filesystem logic.
