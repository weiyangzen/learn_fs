# File Research: sources/os/linux/linux-stable/fs/erofs/fileio.c

## Summary
Implements file-backed EROFS read I/O, allowing filesystem images to be accessed through backing files instead of block devices.

## Main Responsibilities
- Builds read requests as bios backed by `kiocb` file reads.
- Scans folios into mapped, inline, hole, and device-backed segments.
- Copies inline data directly and zeroes holes.
- Submits merged backing-file reads.
- Completes online folio state.

## Key APIs
- `erofs_fileio_bio_alloc()`
- `erofs_fileio_submit_bio()`
- `erofs_fileio_aops`

## Important Behavior
`erofs_fileio_scan_folio()` maps each folio range through `erofs_map_blocks()`, then either copies metadata, zeroes, or appends the folio to a pending backing-file bio-like request. Direct I/O is used when the mount option and backing file allow it.

## Risks
Request lifetime uses both bio completion and explicit refcounting. Partial backing-file reads are treated as I/O errors.
