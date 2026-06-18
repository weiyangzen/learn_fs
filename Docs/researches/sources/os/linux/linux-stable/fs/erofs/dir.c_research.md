# File Research: sources/os/linux/linux-stable/fs/erofs/dir.c

## Summary
Implements EROFS directory iteration.

## Main Responsibilities
- Reads directory data blocks from the inode mapping.
- Validates dirent name offsets and name lengths.
- Emits directory entries.
- Performs directory readahead.
- Synthesizes `.` when the on-disk dot entry is omitted.

## Key APIs
- `erofs_dir_fops`

## Important Behavior
A directory block begins with an array of `struct erofs_dirent`; `de[0].nameoff` gives the end of the dirent array and start of name data. Iteration validates this structure before emitting names.

## Risks
Directory corruption is reported as `-EFSCORRUPTED`. Correctness depends on sorted/packed dirent layout and valid name offsets.
