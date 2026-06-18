# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbittab.c

## Role

`gsbittab.c` defines static lookup tables for Ghostscript bit operations. It is paired with `gsbittab.h`.

This is graphics utility data, not filesystem code.

## Defined Tables

- `byte_reverse_bits[256]`: maps a byte to the same byte with bit order reversed.
- `byte_right_mask[9]`: maps `N` to a byte with `N` trailing one bits.
- `byte_count_bits[256]`: maps a byte to its population count.
- `byte_bit_run_length_0` through `byte_bit_run_length_7`: for each starting bit position, maps a byte to the run length of one bits starting at that bit.
- `byte_bit_run_length[8]`: pointer table for the forward run-length tables.
- `byte_bit_run_length_neg[8]`: pointer table for negative/rotated bit indexing.
- `byte_acegbdfh_to_abcdefgh[256]`: reorders interleaved bit order `acegbdfh` into `abcdefgh`.

## Implementation Notes

- Uses `bit_table_8(...)` from `gsbittab.h` to generate the 256-entry reverse, count, and reorder tables at compile time.
- Uses local macros (`t8`, `r8`, `r16`, `r32`, `r64`, `r128`, `rr8`) to generate run-length tables compactly.
- Run-length values add 8 when the run reaches the low-order bit, indicating that a scan may continue into the next byte.
- Includes `gsbittab_dummy()` because some old C compilers expected executable code in every translation unit.

## Dependencies

- Includes `stdpre.h` and `gsbittab.h`.
- Exports data declared in `gsbittab.h`.

## Notable Risks

- The generated table macro patterns are dense and easy to break if edited manually.
- Consumers must understand the special “run length plus 8” continuation convention.
