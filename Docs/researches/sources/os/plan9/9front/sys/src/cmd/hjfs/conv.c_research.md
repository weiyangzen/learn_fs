# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/conv.c

Packs and unpacks `hjfs` on-disk block formats.

Key points:
- Defines little-endian GET/PUT macros for 8-, 16-, 24-, 32-, and 64-bit fields.
- `unpack()` reads a raw disk block into a typed `Buf`:
  - unknown/default type copies raw data
  - `TSUPERBLOCK` decodes superblock fields
  - `TDENTRY` decodes all dentries in a block
  - `TINDIR` decodes indirect block offsets
  - `TREF` decodes 24-bit reference counts
- `pack()` serializes typed `Buf` contents back into the one-byte type tag plus payload.
- Aborts on unknown block types when packing.

Dependencies and interactions:
- Used by `dev.c` for every block read/write.
- Layout constants come from `dat.h`.

Research relevance:
- Defines the byte-level on-disk format for `hjfs` metadata and data blocks.
