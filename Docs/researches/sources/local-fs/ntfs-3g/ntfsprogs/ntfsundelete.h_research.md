# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsundelete.h

## File Role

`ntfsundelete.h` defines the shared data structures for `ntfsundelete.c`. It contains no function prototypes beyond included library headers; its main purpose is to model command options and recovered MFT-record contents.

## Includes

The header includes:

- `types.h` for NTFS/basic types
- `list.h` for intrusive linked-list heads
- `runlist.h` for `runlist_element`
- `utils.h` for utility types and declarations used by the implementation

## Command Mode and Options

`enum optmode` defines:

- `MODE_NONE`
- `MODE_SCAN`
- `MODE_UNDELETE`
- `MODE_COPY`
- `MODE_ERROR`

`struct options` stores parsed CLI state:

- device path and mode
- scan filters: percentage, match pattern/case, size range, time cutoff, parent display
- undelete selectors and outputs: inode, destination, output filename, fill byte, truncate, optimistic recovery
- copy range: `mft_begin`, `mft_end`
- verbosity and force flags

## Recovered Metadata Structures

`struct filename` represents one `$FILE_NAME` attribute:

- Unicode and locale-converted names
- allocated/data sizes
- file attribute flags
- created/altered/MFT-changed/accessed times
- namespace type
- parent MFT reference and optional resolved parent name

`struct data` represents one `$DATA` stream:

- stream name in locale and Unicode forms
- resident/compressed/encrypted flags
- allocated/data/initialized/VCN sizes
- decompressed runlist
- recoverability percentage
- resident data pointer when applicable

`struct ufile` represents one candidate deleted MFT record:

- inode number and last modification date
- lists of names and data streams
- preferred filename and parent name
- maximum observed size
- flags for attribute-list and directory records
- raw MFT record buffer

## Integration Notes

The implementation initializes `struct ufile.name` and `struct ufile.data` with `NTFS_INIT_LIST_HEAD`, appends `struct filename` and `struct data` entries while parsing MFT records, and releases all owned memory through `free_file()` in `ntfsundelete.c`.

The structs intentionally preserve multiple redundant NTFS size/date/name sources because deleted records may be partially inconsistent and recovery chooses conservative values such as the maximum observed size.
