# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfdtab.c

Generated static lookup tables for the `CCITTFaxDecode` filter.

The file contains four `const cfd_node` arrays:

- `cf_white_decode`.
- `cf_black_decode`.
- `cf_2d_decode`.
- `cf_uncompressed_decode`.

Each entry stores a decoded run/exception value and code length. Positive values are run lengths or table offsets depending on context; negative values use the exceptional codes defined in `scf.h`, such as run errors, EOL/zero runs, uncompressed mode, pass mode, and horizontal mode.

The file also includes `scfdtab_dummy` to satisfy compilers that require executable code in each translation unit.

This is generated compression-table data, not filesystem logic.
