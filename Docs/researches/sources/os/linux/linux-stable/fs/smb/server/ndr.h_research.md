# File Research: sources/os/linux/linux-stable/fs/smb/server/ndr.h

This header declares the ksmbd NDR blob cursor and encoder/decoder APIs for filesystem xattrs.

Definitions:
- `struct ndr`
  - `data`: backing byte buffer.
  - `offset`: current read/write offset.
  - `length`: tracked buffer/input length.
- `NDR_NTSD_OFFSETOF`: constant `0xA0`.

Declared APIs:
- DOS attributes:
  - `ndr_encode_dos_attr()`
  - `ndr_decode_dos_attr()`
- POSIX ACL metadata:
  - `ndr_encode_posix_acl()`
- NT ACL blobs:
  - `ndr_encode_v4_ntacl()`
  - `ndr_encode_v3_ntacl()`
  - `ndr_decode_v4_ntacl()`

Role:
- Shared contract between ksmbd VFS/xattr code and `ndr.c`.

Risk areas:
- The header declares `ndr_encode_v3_ntacl()`, but the implementation is not present in `ndr.c` or the searched SMB server tree. If referenced by future code, this would become a link-time issue unless implemented elsewhere.
- `struct ndr` exposes mutable cursor fields directly; callers must initialize `data`, `offset`, and `length` according to encode/decode mode.
