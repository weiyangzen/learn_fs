# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtifs.c

Implements the shared TIFF page/directory/strip writer used by multiple Ghostscript TIFF output devices.

Key behavior:
- Defines standard TIFF directory entries for page identity, dimensions, strip offsets/counts, orientation, rows per strip, X/Y resolution, planar config, resolution unit, page number, software, and timestamp.
- Defines indirect standard values for next-directory offset, rational resolutions, software string, and TIFF date/time string.
- On big-endian builds, adjusts packed SHORT/BYTE immediate tag values before writing them.
- `gdev_tiff_begin_page` writes the TIFF header for a new file or patches the previous directory pointer for multi-page output.
- Merges sorted standard entries with sorted client entries, replacing standard tags when client tags use the same tag number.
- Computes strip count from `max_strip_size`; uses one strip when no maximum is supplied, otherwise calculates rows per strip with a minimum of one row.
- Allocates paired `StripOffsets` and `StripByteCounts` arrays, writes placeholder strip metadata, records the first strip start, and writes indirect values after directory entries.
- `gdev_tiff_end_strip` records each strip byte count, pads odd file offsets to word alignment, and records the next strip start.
- `gdev_tiff_end_page` records where the next directory pointer lives, patches strip offsets and byte counts back into the file, and frees the strip metadata array.

Dependencies:
- Uses `stdio_.h`, `time_.h`, `gstypes.h`, `gscdefs.h`, `gdevprn.h`, and `gdevtifs.h`.
- Depends on Ghostscript printer helpers for page/file state and scan-line sizing.

Research notes:
- This file provides the core multi-page TIFF chaining and strip-offset patching that higher-level TIFF devices rely on.
- Client-provided TIFF entries must be sorted by tag, as the merge algorithm assumes sorted inputs.
