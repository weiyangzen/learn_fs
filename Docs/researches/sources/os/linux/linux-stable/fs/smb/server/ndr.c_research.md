# File Research: sources/os/linux/linux-stable/fs/smb/server/ndr.c

This file implements a small NDR-like encoder/decoder used for ksmbd extended attribute blobs, including DOS attributes, POSIX ACL metadata, and v4 NT ACL blobs.

Internal helpers:
- `ndr_get_field()`: returns `n->data + n->offset`.
- `try_to_realloc_ndr_blob()`: grows `n->data` by 1024 bytes beyond the requested write area using `krealloc()`, then zeros 1024 bytes from the current offset.
- Write helpers:
  - `ndr_write_int16()`
  - `ndr_write_int32()`
  - `ndr_write_int64()`
  - `ndr_write_bytes()`
  - `ndr_write_string()`
- Read helpers:
  - `ndr_read_string()`
  - `ndr_read_bytes()`
  - `ndr_read_int16()`
  - `ndr_read_int32()`
  - `ndr_read_int64()`

Encoding/decoding:
- `ndr_encode_dos_attr()`
  - Allocates a 1024-byte blob.
  - Encodes DOS attribute xattr formats for version 3 and version 4.
  - Version 3 includes hex string, version fields, flags, attributes, EA size, size, allocation size, create time, and change time.
  - Version 4 encodes empty string, version fields, flags, attributes, inode time, and create time.

- `ndr_decode_dos_attr()`
  - Parses the encoded string and version fields.
  - Supports versions 3 and 4.
  - Verifies the duplicate version field matches.
  - Extracts attributes and relevant timestamps while skipping unused fields.

- `ndr_encode_posix_acl_entry()`
  - Encodes ACL entry count and entry records.
  - Aligns entry payloads to 8 bytes.
  - Writes type twice, optional uid/gid for user/group entries, and permission bits.

- `ndr_encode_posix_acl()`
  - Allocates a 1024-byte blob.
  - Writes reference IDs for access/default ACLs.
  - Encodes mapped inode uid/gid and mode.
  - Appends access ACL and default ACL entries when present.

- `ndr_encode_v4_ntacl()`
  - Allocates a 2048-byte blob.
  - Encodes version, level, reference id, hash type, 64-byte security descriptor hash, description, timestamp, POSIX ACL hash, and raw security descriptor buffer.

- `ndr_decode_v4_ntacl()`
  - Validates version 4 and duplicate version field.
  - Reads level/ref id/hash fields.
  - Reads and validates a 10-byte description prefix against `posix_acl`.
  - Allocates and copies remaining data as the security descriptor buffer.

Declared but absent here:
- `ndr.h` declares `ndr_encode_v3_ntacl()`, but this file does not implement it. In the searched server tree, only `ndr_encode_v4_ntacl()` was found as an implementation.

Dependencies:
- Uses `xattr_dos_attrib`, `xattr_smb_acl`, and `xattr_ntacl` structures from ksmbd xattr/ACL definitions.
- Uses idmapped mount helpers for UID/GID encoding in POSIX ACL blobs.

Risk areas:
- Write helpers reallocate when `n->length <= n->offset + size`; exact-boundary writes trigger growth, which is conservative.
- `try_to_realloc_ndr_blob()` increases `n->length` by exactly 1024 regardless of `sz`, while `krealloc()` requests `offset + sz + 1024`; length accounting can understate the allocated size for large writes.
- Encoder error paths return without freeing `n->data`; callers must free partial blobs after failures.
- Decoder inputs are xattr blobs and must be treated as untrusted; bounds checks are present in primitive readers, but higher-level validation is minimal.
- `ndr_decode_v4_ntacl()` calls `ndr_read_bytes(n, acl->desc, 10)` without checking that return value before `strncmp()`.
