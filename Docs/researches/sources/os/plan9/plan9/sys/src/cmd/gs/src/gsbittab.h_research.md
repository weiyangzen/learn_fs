# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbittab.h

Header for byte-level bit operation lookup tables.

Key contents:
- Defines table-expansion macros:
  - `bit_table_2`
  - `bit_table_4`
  - `bit_table_6`
  - `bit_table_8`
- Declares externally defined tables from `gsbittab.c`:
  - `byte_reverse_bits`
  - `byte_right_mask`
  - `byte_count_bits`
  - `byte_bit_run_length_0` through `_7`
  - `byte_bit_run_length`
  - `byte_bit_run_length_neg`
  - `byte_acegbdfh_to_abcdefgh`

Important implementation notes:
- The table macros compose smaller bit combinations into larger 2/4/6/8-bit transformation tables.
- The run-length table contract is documented here and mirrored by the implementation.
- Consumers depend on `byte` being available from prior Ghostscript base headers.
