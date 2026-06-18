# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcif.c

Ghostscript CIF output driver for generating Caltech Intermediate Form-style chip layout output from rendered monochrome pages.

Key behavior:
- Defines `gs_cif_device` as a 1-bit printer device, defaulting to 72 DPI unless `X_DPI`/`Y_DPI` are overridden.
- `cif_print_page` derives a CIF structure name from the output filename prefix before the first dot, writes CIF prologue records, scans each rendered line, and emits box records for set bits.
- With `TILE` defined, every set bit becomes a `B4 4 ...` box.
- Without `TILE`, consecutive set bits on a scanline are coalesced into wider box records.

Notable dependencies:
- Only uses `gdevprn.h` plus standard string routines available through the Ghostscript environment.

Research notes:
- This is an output conversion device, not storage/filesystem code.
- There is a likely allocation bug: `s` is allocated with `length` bytes and then writes `s[length] = '\0'`; the allocation should allow one extra byte. In the no-dot case, `length` is already `strlen + 1`, then the code writes one byte beyond that.
- The non-`TILE` run coalescing does not flush a run that reaches the end of a scanline, so trailing black runs at line end can be omitted.
