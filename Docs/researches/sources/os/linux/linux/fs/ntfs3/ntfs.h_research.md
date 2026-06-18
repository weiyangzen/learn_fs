# File Research: sources/os/linux/linux/fs/ntfs3/ntfs.h

## Role

Defines NTFS3's on-disk format model: magic values, record layouts, attribute layouts, index records, reparse buffers, EA/security structures, and small helpers for interpreting those packed structures. This header is the low-level contract between NTFS disk bytes and the rest of the Linux `ntfs3` driver.

## Major Contents

- Core constants:
  - `NTFS_NAME_LEN`, `NTFS_LINK_MAX`, LZNT constants, cluster sentinel values such as `SPARSE_LCN`, `RESIDENT_LCN`, `COMPRESSED_LCN`, `DELALLOC_LCN`.
  - MFT record numbers for NTFS metadata files, including `$MFT`, `$MFTMirr`, `$LogFile`, `$Volume`, `$Bitmap`, `$Secure`, `$UpCase`, and `$Extend`.
- On-disk identifiers:
  - `enum ATTR_TYPE` defines NTFS attribute type codes.
  - `enum FILE_ATTRIBUTE` defines Windows/NTFS file attribute bits.
  - `enum NTFS_SIGNATURE` defines record signatures like `FILE`, `INDX`, `BAAD`.
- Fundamental record formats:
  - `struct NTFS_BOOT` is the packed 512-byte boot sector.
  - `struct NTFS_RECORD_HEADER` is the shared fixup-header prefix for FILE/INDX/log records.
  - `struct MFT_REC` models one MFT record.
  - `struct MFT_REF` stores record number plus sequence.
- Attribute formats:
  - `struct ATTRIB` wraps resident and nonresident attribute headers.
  - `struct ATTR_RESIDENT` and `struct ATTR_NONRESIDENT` define the resident/nonresident payload metadata.
  - Helpers include `attr_size`, `attr_ondisk_size`, `attr_name`, `attr_run`, `resident_data_ex`, and flag predicates for sparse/compressed/encrypted/indexed attributes.
- Named NTFS metadata structures:
  - Standard information: `ATTR_STD_INFO`, `ATTR_STD_INFO5`.
  - Attribute list entries: `ATTR_LIST_ENTRY`.
  - File names: `ATTR_FILE_NAME`, `NTFS_DUP_INFO`.
  - Index structures: `NTFS_DE`, `INDEX_HDR`, `INDEX_BUFFER`, `INDEX_ROOT`.
  - Volume info and attribute definition table: `VOLUME_INFO`, `ATTR_DEF_ENTRY`.
  - Object ID, quota, security, reparse, WOF compression, EA, ACL, SID structures.

## Important Invariants

- The file is full of `static_assert`s locking exact structure sizes and offsets. These are essential because most structs directly overlay on-disk bytes.
- NTFS record fixups are expected at either legacy or modern MFT offsets, with `MFTRECORD_FIXUP_OFFSET` currently selecting the older `0x2A` layout.
- Attribute records must distinguish resident and nonresident storage, with nonresident attributes carrying VCN ranges, runlist offsets, allocated/data/valid sizes, and optional total size for sparse/compressed streams.
- Directory/index entries rely on variable-size entries and optional trailing VBN fields, so helpers compute offsets rather than exposing fixed trailing members.
- NTFS time/security/reparse/EA structs are little-endian and intentionally mirror Windows NTFS layouts.

## Dependencies

- Uses Linux kernel endian and type APIs.
- Relies on helper pointer macros from `debug.h`.
- Exposes data structures consumed by nearly every NTFS3 implementation file, especially `record.c`, `run.c`, `super.c`, `xattr.c`, inode, index, and attribute code.

## Notes For Future Work

- This file is schema-critical. Any change must be validated against on-disk compatibility, not just C type safety.
- Several helpers operate on caller-validated buffers. Callers must prove size and bounds before using them.
- `le_cmp()` appears worth extra attention in future review: the name comparison arm uses `!le->name_len` before `memcmp`, which means non-empty names are not compared there. It may be intentional due other ordering checks, but it is surprising.
