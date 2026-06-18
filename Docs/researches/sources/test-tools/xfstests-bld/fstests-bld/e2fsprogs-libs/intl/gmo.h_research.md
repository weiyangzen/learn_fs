<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/gmo.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/gmo.h

## Purpose
This header describes the binary GNU `.mo` message catalog file format used by the loader.

## Important APIs, Types, and Functions
It defines magic values `_MAGIC` and `_MAGIC_SWAPPED`, revision constants, the 32-bit unsigned type `nls_uint32`, `struct mo_file_header`, `struct string_desc`, `struct sysdep_segment`, `struct sysdep_string`, nested `struct segment_pair`, and `SEGMENTS_END`.

## Control Flow
No runtime flow exists in the header. Preprocessor logic chooses an unsigned 32-bit type from `unsigned`, `unsigned short`, or `unsigned long`, intentionally producing a compile-time error if none fits.

## State and Persistence
It models persistent on-disk `.mo` catalog state: header fields, string descriptor tables, hash table offsets, and optional system-dependent string metadata.

## Dependencies and Integration Points
`loadmsgcat.c` reads these structures directly from mapped or malloced `.mo` files, while `gettextP.h` uses `nls_uint32` and descriptor types in loaded-domain structures.

## Risks
The structs mirror file layout and assume 32-bit fields. Any packing/alignment mismatch or unsupported revision can invalidate catalog loading. Offsets from untrusted catalog files must be validated by loader logic.

## Test Signals
Load little-endian and swapped-endian `.mo` fixtures, revision 0 catalogs, minor revision 1 sysdep catalogs, and invalid headers with wrong magic or unsupported major revision.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/gmo.h -->
