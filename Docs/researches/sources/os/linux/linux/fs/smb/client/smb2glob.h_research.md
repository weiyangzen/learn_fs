# File Research: sources/os/linux/linux/fs/smb/client/smb2glob.h

This header defines shared SMB2 constants and small data structures used by SMB2 client implementation files.

Primary contents:
- `enum smb2_compound_ops`: identifiers for the open-operation-close compound helper in `smb2inode.c`.
- Chained request flags: `CHAINED_REQUEST`, `START_OF_CHAIN`, `END_OF_CHAIN`, and `RELATED_REQUEST`.
- `struct status_to_posix_error`: SMB2/NT status code to Linux errno mapping entry, including status string.

Compound operation enum:
- Includes operations for delete disposition, set/query info, query directory, mkdir, rename, hardlink, set EOF, unlink, POSIX query info, set/get reparse point, WSL EA query, and open-query fallback.
- These enum values are consumed by `smb2_compound_op()` to construct SMB2 compound request chains.

Dependencies:
- Basic Linux fixed-width types and SMB2 implementation files that include this header.

Research notes:
- This is a small cross-file contract header. Changes to `enum smb2_compound_ops` must stay synchronized with the switch handling in `smb2inode.c`.
- `status_to_posix_error` is the public shape used by `smb2maperror.c`, generated mapping data, and KUnit test exports.
