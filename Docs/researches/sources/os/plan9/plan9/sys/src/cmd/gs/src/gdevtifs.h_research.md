# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtifs.h

Defines the TIFF types, tag constants, directory-entry representation, TIFF writer state, and public TIFF page/strip writer functions.

Key behavior:
- Defines fixed-size TIFF integer typedefs from architecture size macros rather than assuming C `short`/`long` widths.
- Defines the TIFF header and directory-entry structures, including magic values for big/little endian and TIFF version 42.
- Enumerates TIFF field data types and the internal `TIFF_INDIRECT` flag used to mark values that should be written out-of-line.
- Enumerates the subset of TIFF tags used by these Ghostscript devices, including image dimensions, compression, photometric interpretation, fill order, strip metadata, resolution, T4/T6 fax options, page number, software, date/time, and `CleanFaxData`.
- Defines compression, photometric, orientation, planar configuration, T4/T6 option, resolution-unit, and clean-fax-data constants.
- Defines stack-only `gdev_tiff_state`, tracking memory, directory offsets, tag counts, current strip index/count/rows, patch offsets, and strip offset/count arrays.
- Declares `gdev_tiff_begin_page`, `gdev_tiff_end_strip`, and `gdev_tiff_end_page`.

Dependencies:
- Requires Ghostscript architecture macros, memory type `gs_memory_t`, printer type `gx_device_printer`, and byte/FILE definitions from including source context.

Research notes:
- The header explicitly warns that `gdev_tiff_state` has no GC descriptor and must not live in GC-managed allocated storage.
- The tag list is intentionally partial and grows only as supported devices need more TIFF fields.
