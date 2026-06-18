# File Research: sources/windows/windows-driver-samples/filesys/cdfs/pathsup.c

## Purpose

Implements path-table support for CDFS. The path table is used as a compact breadth-first directory index, enabling directory lookup by parent ordinal and path-table offset.

## Main Entry Points

- `CdLookupPathEntry`
- `CdLookupNextPathEntry`
- `CdFindPathEntry`
- `CdMapPathTableBlock`
- `CdUpdatePathEntryFromRawPathEntry`
- `CdUpdatePathEntryName`

## Path Table Walking

`CdLookupPathEntry` maps the path-table sector containing a known offset, positions the enumeration context, and converts the raw entry into a `PATH_ENTRY`.

`CdLookupNextPathEntry` advances by the current path-entry length, remaps when the cursor moves into the second sector of a mapped two-sector block, detects EOF in the last block, and converts the next raw entry.

`CdFindPathEntry` searches child directory entries under a parent FCB. It starts from the cached first-child offset when available, otherwise from the parent path-table entry. It caches `ChildPathTableOffset` and `ChildOrdinal` once discovered. It raises corruption if a parent ordinal exceeds the 16-bit on-disk parent backpointer limit.

## Mapping and Validation

`CdMapPathTableBlock` maps two sectors at a time through the cache manager. If the two-sector range crosses a VACB view boundary, it allocates an auxiliary buffer, maps each sector separately, copies them together, and unpins each map.

`CdUpdatePathEntryFromRawPathEntry` reads raw name length, disk offset, XAR adjustment, parent ordinal, entry length, and raw directory-name pointer. It validates bounds in the last data block. A zero-length name is normally corruption, but the code treats it as EOF when the last path-table block length is block-aligned, preserving compatibility with some Video CD media.

## Name Handling

`CdUpdatePathEntryName` converts a raw path-table directory id into `CD_NAME` fields. It handles self-entry name `0` as a hard-coded directory name, converts OEM to Unicode for non-Joliet media, converts big-endian Unicode for Joliet, strips a trailing period, and optionally builds an uppercase comparison name.

## Dependencies

Uses path-table raw macros, cache-manager mapping, CDFS name conversion, path-entry memory management, VCB Joliet state, and FCB child-offset caching.
