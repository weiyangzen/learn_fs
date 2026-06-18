# File Research: sources/local-fs/e2fsprogs/misc/e2freefrag.8.in

## Purpose
Manual page template for `e2freefrag`, which reports free-space fragmentation on ext2/3/4 filesystems.

## Documented Interface
- Synopsis: `e2freefrag [-c chunk_kb] [-h] filesys`
- `-c chunk_kb`: report aligned free chunks of a given power-of-two size in KB.
- `-h`: usage.

## Output Described
- Device and block size.
- Total and free block counts.
- Optional total/free chunk counts.
- Minimum, maximum, average free extent size.
- Histogram of free extent sizes.

## Notes
- Explains that the report helps estimate free-space fragmentation.
- See also: `debugfs`, `dumpe2fs`, `e2fsck`.
