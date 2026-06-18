# File Research: sources/os/linux/linux/fs/smb/server/ndr.h

This compact header declares the NDR blob cursor and encoder/decoder entry points.

Key declarations:
- `struct ndr` carries `data`, current `offset`, and total `length`.
- `NDR_NTSD_OFFSETOF` defines the NT security descriptor offset constant used by related ACL code.
- Public APIs cover DOS attribute encode/decode, POSIX ACL encode, v3/v4 NT ACL encode, and v4 NT ACL decode.

Role in this group:
- `ndr.c` implements all declared functions.
- Callers provide filesystem xattr-side structures such as `xattr_dos_attrib`, `xattr_smb_acl`, and `xattr_ntacl`.
- The header intentionally exposes only high-level serialization calls, keeping primitive read/write helpers private to `ndr.c`.
