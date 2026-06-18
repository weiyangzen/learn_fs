# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfdgen.c

Generator program for `scfdtab.c`, the CCITTFax decode lookup tables.

The program opens `scfdtab.c` for writing and emits:

- Header/license comments.
- Includes for `std.h`, `scommon.h`, and `scf.h`.
- `cf_white_decode`, `cf_black_decode`, `cf_2d_decode`, and `cf_uncompressed_decode` tables.
- A dummy function for compilers requiring executable code.

The generator builds first-level and second-level decode trees by enumerating the encode tables from `scfetab.c`/`scf.h`:

- White and black termination/makeup codes.
- 1-D uncompressed and EOL-related codes.
- 2-D pass, horizontal, vertical, uncompressed, and EOL-related codes.
- Uncompressed mode and exit codes.

It uses `malloc` for second-level nodes while generating output.

This is build-time table generation for CCITT fax decoding, not filesystem implementation.
