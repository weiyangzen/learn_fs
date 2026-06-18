# File Research: sources/os/linux/linux/fs/smb/server/ndr.c

This file implements ksmbd’s local NDR-style little-endian encoder/decoder for DOS attributes, POSIX ACL metadata, and NT ACL xattrs.

Internal marshalling helpers:
- `ndr_get_field()` returns the current cursor.
- `try_to_realloc_ndr_blob()` grows the blob by 1024 bytes and zeroes the new region.
- `ndr_write_int16/int32/int64`, `ndr_write_bytes`, and `ndr_write_string` append little-endian values or aligned strings.
- `ndr_read_int16/int32/int64`, `ndr_read_bytes`, and `ndr_read_string` bounds-check reads against `n->length`.

DOS attribute handling:
- `ndr_encode_dos_attr()` allocates a 1024-byte blob and writes versioned DOS xattr data. Version 3 includes hex attr text, EA size, size, allocation size, create time, and change time; version 4 writes internal time and create time.
- `ndr_decode_dos_attr()` validates supported versions 3 and 4, checks duplicate version fields match, and extracts attributes and timestamps.

ACL handling:
- `ndr_encode_posix_acl()` writes optional access/default ACL references, mapped inode uid/gid through the mount idmap, mode, and ACL entries.
- `ndr_encode_v4_ntacl()` writes version, hash metadata, description, current time, POSIX ACL hash, and raw security descriptor.
- `ndr_decode_v4_ntacl()` validates version 4, verifies the description starts with `posix_acl`, allocates `sd_buf`, and copies the remaining security descriptor.

Risk/edge notes:
- Encoder functions allocate `n->data`; ownership is transferred to callers.
- Some error paths after allocation return without freeing `n->data`, so callers must treat partial encode failures carefully or the caller path must clean up.
- Decode functions consistently reject short buffers via offset/length checks.

Role in this group:
- Declared by `ndr.h`.
- Supplies serialization used by ksmbd VFS/xattr ACL paths rather than direct network SMB2 packet processing.
