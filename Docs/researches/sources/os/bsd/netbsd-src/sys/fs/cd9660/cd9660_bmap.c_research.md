# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_bmap.c

## Summary
Implements logical-to-physical block mapping for CD9660 files.

## Main Responsibilities
- Return the underlying device vnode when requested.
- Convert logical file block numbers to device block numbers using `iso_start`, mount block shift, and `DEV_BSHIFT`.
- Compute limited read-ahead run length based on file size and `MAXBSIZE`.

## Key Interfaces
- `cd9660_bmap(void *v)` vnode operation.

## Risks
The mapping assumes ISO files are contiguous extents. Correctness depends on `iso_start`, `i_size`, and mount block shift being initialized correctly.
