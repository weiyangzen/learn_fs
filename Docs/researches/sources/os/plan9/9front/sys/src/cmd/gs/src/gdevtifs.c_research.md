# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtifs.c

## Purpose
Shared TIFF-writing substructure for Ghostscript printer devices. It writes TIFF headers/directories, manages strip offset/count arrays, records strip sizes, and patches directory fields after image data is written.

## Main Concepts
- Defines standard TIFF directory entries for page type, dimensions, strip offsets, orientation, rows per strip, byte counts, resolution, planar config, page number, software, and timestamp.
- Merges caller-supplied sorted TIFF entries with standard entries, allowing caller entries to replace standard tags.
- Stores strip offsets and byte counts in allocated arrays until page finalization.
- Supports multi-page output by patching the previous directory’s next-directory pointer.

## Key Functions
- `gdev_tiff_begin_page`: writes TIFF header for a new file, writes merged directory entries and indirect values, allocates strip arrays, computes rows per strip, and records first strip start.
- `gdev_tiff_end_strip`: records current strip byte count, pads the file to word alignment, and records the next strip offset.
- `gdev_tiff_end_page`: seeks back to patch strip offsets and byte counts, frees strip arrays, and remembers the next directory pointer location.

## Dependencies
Uses Ghostscript types, printer helpers, product/revision metadata, and standard C file/time APIs.

## Notable Risks
- Heavy use of `ftell`, `fseek`, and native integer layout makes portability dependent on classic TIFF assumptions and platform type sizes.
- Allocation failure after writing part of a directory leaves a partially written output.
- The initial placeholder write uses uninitialized strip arrays before they are filled, though those bytes are later patched.
- Local time generation uses `localtime` without null checking.
- Return values from file I/O are mostly ignored.

## Filesystem Relevance
Directly performs seekable file writes for TIFF output. It is output-format infrastructure, not filesystem implementation logic.
