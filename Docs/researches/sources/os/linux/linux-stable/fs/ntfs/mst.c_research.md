# File Research: sources/os/linux/linux-stable/fs/ntfs/mst.c

`mst.c` implements NTFS multi-sector transfer protection fixups. These protect metadata records spanning 512-byte sectors by replacing each sector’s final word with an update sequence number before write and restoring original words after read.

Key functions:
- `post_read_mst_fixup()` validates update-sequence placement/count, checks each protected sector trailer against the stored USN, marks corrupted records with `magic_BAAD`, and restores original trailer words from the update sequence array.
- `pre_write_mst_fixup()` validates the record, increments the USN while skipping `0` and `0xffff`, saves each sector trailer into the update sequence array, and writes the USN into each sector trailer.
- `post_write_mst_fixup()` quickly restores the in-memory original trailer words after a known-good pre-write fixup path.

Behavioral details:
- `post_read_mst_fixup()` treats missing/invalid USA metadata as “not protected” and returns success.
- `pre_write_mst_fixup()` treats missing/invalid USA metadata as an error because write protection cannot be applied.
- Incomplete transfer detection logs ratelimited metadata context including magic, MFT number, base MFT reference, in-use flag, observed data word, and expected USN.

Dependencies:
- Uses NTFS record layout definitions from `ntfs.h`.
- MFT read/write paths in `mft.c` rely on these functions before validation and before block I/O.
