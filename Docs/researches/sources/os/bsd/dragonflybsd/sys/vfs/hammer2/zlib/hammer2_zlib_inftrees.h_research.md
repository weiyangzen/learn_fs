# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inftrees.h

Source read: complete file, 62 lines.

Purpose: Internal inflate Huffman-table header. It defines the compact decode entry format, table-size constants, code type enum, and `inflate_table()` prototype.

Key definitions:
- `typedef struct code { unsigned char op; unsigned char bits; unsigned short val; } code;` stores a literal, length/distance base, end marker, invalid marker, or sub-table link.
- `ENOUGH_LENS`, `ENOUGH_DISTS`, and `ENOUGH` size the dynamic table area used inside `struct inflate_state`.
- `codetype` distinguishes code-length (`CODES`), literal/length (`LENS`), and distance (`DISTS`) table generation.

Integration:
- Shared by `hammer2_zlib_inflate.c`, `hammer2_zlib_inftrees.c`, and `hammer2_zlib_inflate.h`.

Risks and review notes:
- The constants are tightly coupled to root table sizes of 9 bits for literal/length and 6 bits for distance tables. Changing those call sites requires recalculating constants.
