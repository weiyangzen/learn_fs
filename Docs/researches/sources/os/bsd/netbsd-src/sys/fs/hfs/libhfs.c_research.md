# File Research: sources/os/bsd/netbsd-src/sys/fs/hfs/libhfs.c

## Purpose
Implements the core HFS+/HFSX on-disk parser used by the kernel HFS filesystem: volume open, wrapper detection, journal metadata reading, catalog and extents B-tree traversal, directory listing, hardlink resolution, structure decoding, extent reads, key comparison, callbacks, and case-folding table construction.

## Main Entry Points
- `hfslib_init()` stores global callbacks and prepares catalog keys for HFS+ private objects.
- `hfslib_open_volume()` opens the device through callbacks, reads the HFS+ volume header or embedded HFS wrapper, reads catalog/extents header nodes, selects key comparison mode, reads journal metadata, creates casefolding table when needed, and stores the volume name.
- `hfslib_close_volume()` closes the callback device.
- `hfslib_find_catalog_record_with_key()` traverses catalog B-tree index and leaf nodes using the volume’s key comparator.
- `hfslib_find_catalog_record_with_cnid()` resolves a CNID through its parent thread, then searches by catalog key.
- `hfslib_find_extent_record_with_key()` traverses the extents overflow B-tree.
- `hfslib_get_file_extents()` combines inline fork extents with overflow records until the fork’s total blocks are covered.
- `hfslib_get_directory_contents()` finds children by parent CNID, walks linked leaf nodes, filters private objects, and returns child records and names.
- `hfslib_is_journal_clean()` treats unjournaled volumes as clean and journaled volumes as clean only when journal start equals end.
- `hfslib_read_*()` routines decode big-endian volume headers, HFS wrapper MDBs, B-tree nodes, catalog records, extent records, fork descriptors, Unicode strings, BSD metadata, Finder info placeholders, and journal structures.
- `hfslib_readd_with_extents()` reads logical file ranges by intersecting requested ranges with extent descriptors.
- Callback wrappers centralize error, allocation, open, close, and read operations.
- `hfslib_compare_catalog_keys_cf()`, `hfslib_compare_catalog_keys_bc()`, and `hfslib_compare_extent_keys()` implement B-tree key ordering.
- `hfslib_create_casefolding_table()` lazily allocates a static HFS+ case-fold table.
- `hfslib_get_hardlink()` resolves HFS+ hardlink catalog records in the private metadata directory.

## Dependencies
Depends on `libhfs.h` on-disk structures and callbacks supplied by kernel glue in `hfs_subr.c`. Uses HFS+ B-tree, catalog, extent, journal, and wrapper format definitions.

## Risks and Notes
This is a parser-heavy file with many trust boundaries on disk data. Several source comments mark incomplete or suspect behavior: extent index records are described as bogus, Finder info readers are placeholders, binary catalog comparison is byte-based despite the spec requiring 16-bit chunks, and casefolding has endian caveats. `hfslib_read_unistr255()` clamps excessive name length to 255 but does not skip over the original on-disk length, which could desynchronize parsing on malformed input. B-tree traversal assumes consistent node ordering and valid record offsets. `hfslib_readd_with_extents()` does not zero gaps for sparse or missing coverage; it only reads intersections. The library uses process-global callbacks and casefolding state, so initialization order matters.
