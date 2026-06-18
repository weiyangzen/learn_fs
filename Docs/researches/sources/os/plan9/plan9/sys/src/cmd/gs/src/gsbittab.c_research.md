# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbittab.c

Defines constant byte lookup tables used by Ghostscript bit operations.

Key contents:
- Includes `stdpre.h` and `gsbittab.h`.
- Defines `byte_reverse_bits[256]` using `bit_table_8`.
- Defines `byte_right_mask[9]` for trailing-bit masks from 0 through 8 bits.
- Defines `byte_count_bits[256]` for population count of each byte.
- Defines `byte_bit_run_length_0` through `_7`, each indexed by byte value and representing run length of 1 bits starting at a bit position.
- Defines pointer tables:
  - `byte_bit_run_length[8]`
  - `byte_bit_run_length_neg[8]`
- Defines `byte_acegbdfh_to_abcdefgh[256]`, a bit-lane permutation table.
- Ends with `gsbittab_dummy()` for compilers that require executable code in each compilation unit.

Important implementation notes:
- The tables are generated through C macros rather than handwritten 256-entry literals.
- Run-length tables encode continuation by adding 8 when the run reaches the low-order bit and may continue into the next byte.
- This file supplies shared static lookup data for low-level bitmap scanning and transformation code.
