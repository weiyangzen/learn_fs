# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_subr.c

Contains the main NTFS implementation helpers: ntnode loading/lifetime, attribute parsing, directory lookup/enumeration, attribute I/O, compression dispatch, fixups, and uppercase table management.

Key points:
- Attribute access:
  - `ntfs_loadntnode()` reads an MFT record, applies multi-sector fixups, parses attributes, and builds the in-memory `ntvattr` list.
  - `ntfs_attrtontvattr()` converts resident and nonresident attributes to internal form, expanding runlists for nonresident data.
  - `ntfs_ntvattrget()` finds attributes by type/name/VCN and follows `$ATTRIBUTE_LIST` records when attributes live in extension records.
- Node lifecycle:
  - `ntfs_ntlookup()` finds or allocates an `ntnode`, initializes locks, inserts into hash, and returns it busy/owned.
  - `ntfs_ntget()`, `ntfs_ntput()`, `ntfs_ntref()`, and `ntfs_ntrele()` manage busy state and use counts.
  - `ntfs_freentvattr()` frees resident data or run arrays.
- Name handling:
  - Unicode/ASCII comparisons use mount callbacks and the `$UpCase` table.
  - `ntfs_ntlookupattr()` parses names containing NTFS alternate data stream syntax.
- Directory lookup:
  - `ntfs_ntlookupfile()` searches `$INDEX_ROOT:$I30`, descends into `$INDEX_ALLOCATION:$I30`, and can fall back to full-tree scan.
  - Supports alternate attribute lookup via `filename:attribute` syntax.
- Directory enumeration:
  - `ntfs_ntreaddir()` reads index root entries first, then scans active index-allocation blocks based on `$BITMAP:$I30`.
  - Caches last enumeration position in `fnode`.
- Attribute I/O:
  - `ntfs_readntvattr_plain()` reads resident data, nonresident run data, and sparse holes.
  - `ntfs_readattr_plain()` spans multiple attribute extents.
  - `ntfs_readattr()` validates ranges and dispatches compressed reads through `ntfs_uncompunit()`.
  - `ntfs_writentvattr_plain()` and `ntfs_writeattr_plain()` support in-place writes to nonresident attributes, but not resident attributes or extension past EOF.
- Fixups and tables:
  - `ntfs_procfixups()` validates and applies NTFS update-sequence fixups.
  - `ntfs_toupper_use()` loads `$UpCase` once globally and reference-counts it across mounts.

Risk/notes:
- This is legacy kernel filesystem code with many direct on-disk structure casts.
- Some write support exists for existing nonresident data, but allocation, truncation, creation, and metadata updates are not implemented in this grouped set.
