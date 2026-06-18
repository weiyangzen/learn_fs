# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/debugreiserfs.h

Shared header for `debugreiserfs`.

Defines:
- Operation modes such as dump, corrupt, scan, recover, pack, unpack, stat, bad-block extraction, file-map, and zero.
- Print/behavior option bits.
- Binary pack format magic values for leaves, full blocks, unformatted bitmap, map records, separated journals, and stream end.
- Packed-item bit masks describing which key/item fields are serialized.
- Packed directory-entry format and masks.
- `struct debugreiserfs_data`, stored in `fs->fs_vp`.
- Accessor macros such as `debug_mode(fs)`, `scan_area(fs)`, `map_file(fs)`, and `be_quiet(fs)`.
- Cross-file function prototypes for stat, corruption, recover, scan, unpack, and map printing.
- `struct saved_item`, used by scan/recover map workflows.

Important format detail: `struct packed_item` compresses item type, mask, and item length into one 32-bit field using bitfield helper macros.

Notable quirks:
- `INTERNAL_START_MAGIC` is defined twice without a value.
- `fread8` is defined twice.
- Serialization macros increment global `sent_bytes`, tying the header tightly to `pack.c`.
