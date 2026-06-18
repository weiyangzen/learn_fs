# File Research: sources/windows/reactos/drivers/filesystems/cdfs/pathsup.c

Implements CDFS ISO-9660 path-table traversal. The path table is used as a compact breadth-first directory index, with directory ordinals and parent ordinals used to locate children without scanning full directory contents first.

Key entry points:
- `CdLookupPathEntry()` maps the path-table block containing a known entry offset and decodes the raw entry into a `PATH_ENTRY`.
- `CdLookupNextPathEntry()` advances by the current entry length, remaps the next two-sector window when needed, and decodes the next ordinal.
- `CdFindPathEntry()` scans child path-table entries for a parent directory, caches the first-child offset/ordinal in the parent FCB, converts candidate names, and compares them against the requested directory name.
- `CdMapPathTableBlock()` maps two sectors through cache manager, or copies two one-sector mappings into an auxiliary buffer when the window crosses a VACB boundary.
- `CdUpdatePathEntryFromRawPathEntry()` validates and translates raw path-table fields into the common in-memory representation.
- `CdUpdatePathEntryName()` converts raw directory names into `CD_NAME` structures for ISO/OEM or Joliet big-endian Unicode names.

Core mechanics:
- Path-table entries are read in two-sector windows because entries can span sector boundaries.
- `LastDataBlock` and `DataLength` bound parsing of the final mapped path-table block.
- Parent ordinals drive child-range scanning; children of a parent are contiguous because the table is breadth-first.
- The parent FCB caches `ChildPathTableOffset` and `ChildOrdinal` after the first child is found, avoiding repeat scans from the parent entry.
- ISO names are converted with `RtlOemToUnicodeN`; Joliet names are byte-swapped from big-endian to little-endian.
- The self/root entry with one zero byte is mapped to the hard-coded directory name.

Important invariants:
- Path-table parent ordinals are 16-bit on disk, so searching children of an FCB with ordinal greater than `MAXUSHORT` raises disk corruption.
- A zero-length path-table name is normally corrupt, except for a compatibility workaround when the final table block is padded to a block boundary.
- Parsed `PathEntryLength` is word-aligned.
- Directory path-table names have no version string.

Filesystem relevance:
- This file is the fast directory-discovery layer used before full directory-entry enumeration.
- Correct path-table parsing controls directory opens and the construction of directory FCBs.

Notable risks:
- Corrupt path-table bounds, zero-length records, or illegal parent ordinals raise hard disk-corruption statuses.
- Auxiliary path-table buffers must be freed/remapped correctly when crossing cache view boundaries.
