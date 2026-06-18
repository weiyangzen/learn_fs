# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsinfo.c

## Role

`ntfsinfo.c` implements the `ntfsinfo` utility. It mounts an NTFS volume read-only, optionally dumps volume-wide metadata, resolves an inode number or path, and prints the MFT record plus decoded NTFS attributes.

## Command-Line Contract

Supported options include:

- `-i/--inode NUM`
- `-F/--file FILE`
- `-m/--mft`
- `-t` for no timestamps
- `-f/--force` to mount with recovery
- `-q`, `-v`, `-V`, `-h`

The long option `--notime` is wired to parser case `T`, which emits a deprecation/error message; lowercase `-t` is the option that actually sets `opts.notime`.

## Control Flow

1. `main()` sets line-buffered stdout and stderr logging.
2. `parse_options()` validates that a device is present and at least one of inode, file, or `--mft` was requested.
3. The volume is mounted read-only through `utils_mount_volume()`, with `NTFS_MNT_RECOVER` if forced.
4. `ntfs_dump_volume()` runs when `opts.mft` is set.
5. If a path or inode is requested, the code opens it with `ntfs_pathname_to_inode()` or `ntfs_inode_open()`.
6. It prints MFT record-level data via `ntfs_dump_inode_general_info()`.
7. It enumerates all attributes with `ntfs_attr_lookup()` and dispatches type-specific dumpers in `ntfs_dump_file_attributes()`.

## Volume Dumping

`ntfs_dump_volume()` reports device state, volume flags/version, sector and cluster sizes, index block size, MFT zone state, `$MFTMirr`, `$AttrDef`, `$Bitmap`, free cluster count, and `$LogFile` state. `$LogFile` details are obtained by opening `FILE_LogFile` and calling `ntfs_check_logfile()`.

## Attribute Dumping

Implemented dumpers cover:

- `$STANDARD_INFORMATION`: timestamps, file attributes, owner/security/quota fields for 72-byte records.
- `$ATTRIBUTE_LIST`: verbose attribute-list entry dump.
- `$FILE_NAME`: parent reference, times, sizes, flags, namespace, filename, reparse tag or EA length.
- `$OBJECT_ID`: object and birth GUIDs.
- `$SECURITY_DESCRIPTOR`: owner/group SIDs plus SACL/DACL ACEs.
- `$VOLUME_NAME` and `$VOLUME_INFORMATION`.
- `$DATA`: metadata-specific verbose handling for `$Secure::$SDS` and `$LogFile`.
- `$INDEX_ROOT` and `$INDEX_ALLOCATION`: index type detection, headers, entries, INDX block fixups, and totals.
- `$REPARSE_POINT`: tag, type name, data length, and first bytes.
- `$EA_INFORMATION` and `$EA`: extended attribute summary and verbose value dump.
- `$LOGGED_UTILITY_STREAM`: verbose hex dump.
- Unknown resident attributes: first 128 bytes are hex dumped.

`$BITMAP` and `$PROPERTY_SET` are placeholders.

## Index And Security Handling

The code recognizes directory `$I30`, `$Secure` indexes (`$SII`, `$SDH`), `$ObjId`, `$Quota`, and `$Reparse` index names. For `$Secure::$SDS`, it opens `$SDS`, walks `$SII`, reads descriptor records by offset, and dumps their security descriptors.

## Risk Areas

- This is a read-only utility, but it casts on-disk structures directly and has limited bounds checking in several dumpers.
- Several TODOs remain, especially around incomplete attribute support, error checking, formatting, ACLs, and indexed attribute coverage.
- `ntfs_dump_attr_ea()` and `ntfs_dump_attr_security_descriptor()` contain comments saying fragmented mapping-pair cases are not fully handled.
- Recursive index dumping depends on bitmap bits and index block reads; damaged metadata can stop dumping early.
- The `--notime` long option mismatch is user-visible.
