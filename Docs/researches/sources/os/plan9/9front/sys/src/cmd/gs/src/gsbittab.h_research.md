# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbittab.h

## Role

`gsbittab.h` declares Ghostscript bit-operation lookup tables and provides compile-time table generator macros.

This is graphics utility infrastructure, not filesystem code.

## Macro Interfaces

- `bit_table_2`
- `bit_table_4`
- `bit_table_6`
- `bit_table_8`

These macros expand weighted bit combinations into complete lookup tables for 2, 4, 6, or 8 input bits.

## Exported Tables

- `byte_reverse_bits[256]`
- `byte_right_mask[9]`
- `byte_count_bits[256]`
- `byte_bit_run_length_0` through `byte_bit_run_length_7`
- `byte_bit_run_length[8]`
- `byte_bit_run_length_neg[8]`
- `byte_acegbdfh_to_abcdefgh[256]`

## Important Semantics

- `byte_bit_run_length_N[B]` uses bit numbering `01234567` within the byte.
- If a one-bit run reaches the low-order bit and could continue into the next byte, the table value is increased by 8.
- `byte_bit_run_length_neg[N]` aliases `byte_bit_run_length[-N & 7]`.

## Dependencies

- Requires Ghostscript’s `byte` type to be visible to users of the extern declarations.

## Notable Risks

- The table-generation macros rely on positional argument naming (`v80`, `v40`, etc.) and are not self-checking.
