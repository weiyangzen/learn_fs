# File Research: sources/os/plan9/9front/sys/src/cmd/sum.c

`sum.c` implements checksum variants compatible with Plan 9 historical `sum`.

Modes:
- Default: 32-bit CRC using `crc_table`.
- `-r`: old research Unix rotating 16-bit sum with 1024-byte block count.
- `-5`: System V-style additive 16-bit sum with 512-byte block count.

Flow:
- `main` selects a `Sumfn`, then processes each file or stdin.
- `sumfile` reads in 8 KiB chunks, accumulates file size and checksum, calls the selected function with `buf == 0` to finalize/print, then appends the file name when present.
- Errors set `exitstr` and continue with remaining files.

Algorithms:
- `sum5` adds bytes and folds high bits into 16 bits at finalization.
- `sumr` rotates right through bit 15 before adding each byte.
- `sum32` updates CRC per byte and, at finalization, incorporates a length-derived four-byte value before printing CRC and size.

Risks:
- Final `sum32` length encoding casts the full `uvlong` size to `int n`, so very large files lose high size bits in the final length mix, matching existing behavior but worth noting.
