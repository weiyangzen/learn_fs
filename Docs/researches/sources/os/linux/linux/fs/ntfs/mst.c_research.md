# File Research: sources/os/linux/linux/fs/ntfs/mst.c

Implements NTFS Multi Sector Transfer protection fixups.

Key functions:
- `post_read_mst_fixup()` validates the update sequence array, detects incomplete multi-sector transfers, marks bad records as `BAAD`, and restores original sector-end words.
- `pre_write_mst_fixup()` increments the update sequence number, stores original sector-end words into the USA, and writes the sequence value into each protected sector tail before disk write.
- `post_write_mst_fixup()` restores protected words after a pre-write fixup without validation.

Semantics:
- `post_read_mst_fixup()` treats absent/invalid USA as “not protected” and returns success.
- `pre_write_mst_fixup()` treats absent/invalid USA as an error because callers must prepare a valid record header.
- Update sequence numbers skip `0` and `0xffff`.

Important dependencies:
- NTFS layout constants and record magic helpers from `ntfs.h`.
- Ratelimited logging for incomplete transfer diagnostics.
