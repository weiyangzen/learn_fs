# File Research: sources/virtualization/nbdkit/filters/cow/cow.h

Purpose: tiny shared declaration for COW block size.

Key details:
- Declares external `unsigned blksize`.
- Included by COW block and filter implementation files.

Integration notes:
- Keeps block size as shared mutable configuration between `cow.c` and `blk.c`.
