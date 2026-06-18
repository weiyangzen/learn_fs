# File Research: sources/os/linux/linux-stable/fs/befs/datastream.c

This file maps BeFS logical file blocks and byte offsets to disk block runs, then reads data through buffer heads. It handles direct, indirect, and double-indirect datastream regions.

Exports:
- `BAD_IADDR` is the zero block-run sentinel.
- `befs_read_datastream()` returns a `buffer_head` containing data at a byte offset and optionally reports the byte offset within the buffer.
- `befs_fblock2brun()` maps a logical file block to a BeFS block run.
- `befs_read_lsymlink()` reads long symlink contents from a datastream into a caller buffer.
- `befs_count_blocks()` estimates VFS `i_blocks`, including inode and indirect metadata blocks.

Mapping logic:
- Direct region: `befs_find_brun_direct()` linearly searches the 12 direct block runs and adjusts returned `start/len` so the requested block is the first returned block.
- Indirect region: `befs_find_brun_indirect()` reads each block in the indirect run, scans disk block-run entries, endian-converts the matching run, and adjusts by offset.
- Double-indirect region: `befs_find_brun_dblindirect()` computes indexes into the double-indirect and indirect levels using `BEFS_DBLINDIR_BRUN_LEN`, reads only the needed metadata blocks, then adjusts the result by logical offset.

Integration:
- `linuxvfs.c` calls `befs_fblock2brun()` from `befs_get_block()`.
- `btree.c` calls `befs_read_datastream()` to read B+tree metadata and nodes.
- `linuxvfs.c` calls `befs_read_lsymlink()` for long symlink folios.
- `befs_count_blocks()` is used when populating VFS inode block counts.

Risk notes:
- The double-indirect code computes `indir_indx = dblindir_leftover / diblklen`; based on the surrounding comments and variables, this looks suspicious because the second-level index would normally divide by the per-indirect-entry data length, not the double-indirect span.
- Double-indirect bounds checks use `>` against lengths; if indexes are equal to length, that is also out of range.
- Indirect mapping trusts disk block-run arrays after minimal validation; corrupt metadata can drive bad run lengths or arithmetic.
- `befs_read_lsymlink()` copies `bh->b_data` whole-block chunks and relies on caller-provided length validation.
