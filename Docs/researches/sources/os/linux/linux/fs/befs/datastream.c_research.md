# File Research: sources/os/linux/linux/fs/befs/datastream.c

## Purpose
Maps BeFS datastream logical file blocks to physical block runs and reads datastream-backed data. This is the block mapping layer used by regular file reads, symlink reads, and B+tree reads.

## Main Functions
- `befs_read_datastream()`: converts byte position to logical file block, maps it with `befs_fblock2brun()`, reads the resulting block run through `befs_bread_iaddr()`, and optionally returns the offset within the buffer.
- `befs_fblock2brun()`: dispatches logical block mapping to direct, indirect, or double-indirect lookup based on datastream range limits.
- `befs_read_lsymlink()`: sequentially reads long symlink contents from a datastream into a caller buffer.
- `befs_count_blocks()`: estimates file space usage in filesystem blocks, including inode and indirect metadata.
- `befs_find_brun_direct()`: linear search through the inode’s direct block-run array; adjusts returned run to begin at the requested block.
- `befs_find_brun_indirect()`: reads indirect block-run blocks and linearly searches their entries.
- `befs_find_brun_dblindirect()`: computes indexes into double-indirect and indirect blocks for the fixed-size double-indirect region and reads only the needed mapping blocks.

## Constants
- `BAD_IADDR = {0, 0, 0}` is exported as a sentinel invalid inode/block address.

## Notable Details
- Direct and indirect regions map variable-length block runs, requiring linear accumulation.
- Double-indirect mapping assumes data block runs and indirect blocks are organized around `BEFS_DBLINDIR_BRUN_LEN`.
- Metadata block counting assumes indirect blocks in the double-indirect region are also fixed-length.

## Risks
- The double-indirect index calculation uses `indir_indx = dblindir_leftover / diblklen`; given surrounding comments, this is a sensitive calculation and likely worth cross-checking against BeFS format expectations.
- The code trusts datastream range fields from disk after inode conversion; corrupted ranges can push mapping into invalid block reads, with errors surfaced through `BEFS_ERR`.
