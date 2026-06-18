# File Research: sources/os/linux/linux-stable/fs/erofs/namei.c

## Summary
Implements EROFS directory name lookup using sorted directory blocks and binary search.

## Main Responsibilities
- Compares lookup names against on-disk names.
- Binary-searches candidate directory blocks.
- Binary-searches dirents inside the target block.
- Converts dirents to NIDs and file types.
- Provides directory inode operations.

## Key APIs
- `erofs_namei()`
- `erofs_dir_iops`

## Important Behavior
EROFS directory entries are sorted alphabetically, so lookup first binary-searches blocks by their first names, then searches within the selected block. Prefix match lengths are reused to reduce repeated comparisons.

## Risks
Lookup assumes valid sorted directory data. Corrupt blocks with no dirents or invalid name offsets produce `-EFSCORRUPTED`; overlong lookup names fail with `-ENAMETOOLONG`.
