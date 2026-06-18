# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtifs.h

## Purpose
Defines TIFF data structures, constants, tags, and the shared state/API for Ghostscript TIFF writers.

## Main Contents
- Defines fixed-size TIFF integer aliases using Ghostscript architecture-size macros.
- Defines `TIFF_header`, endian magic constants, version value, and `TIFF_dir_entry`.
- Enumerates TIFF field types, including internal `TIFF_INDIRECT`.
- Enumerates the subset of TIFF tags used by Ghostscript output devices, including image dimensions, compression, photometric interpretation, fill order, strips, resolution, planar config, fax options, page number, software, and timestamp.
- Defines compression, photometric, fill-order, orientation, planar-config, fax-option, and resolution-unit constants.
- Defines `gdev_tiff_state`, holding memory, directory offsets, strip counts, rows per strip, and strip offset/count arrays.
- Declares `gdev_tiff_begin_page`, `gdev_tiff_end_strip`, and `gdev_tiff_end_page`.

## Dependencies
Relies on Ghostscript architecture macros and printer/file types supplied by including modules.

## Notable Risks
The TIFF state is documented as stack-only because it has no GC descriptor. Allocating it in GC-managed storage would make pointer tracing unsafe.

## Filesystem Relevance
Defines structures for seekable TIFF output files. It is not filesystem implementation code.
