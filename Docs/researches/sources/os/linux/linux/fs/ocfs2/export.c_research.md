# File Research: sources/os/linux/linux/fs/ocfs2/export.c

NFS export support for OCFS2. This file implements `struct export_operations` so NFS file handles can be encoded, decoded, and reconnected to dentries safely across a clustered filesystem.

File handle format:
- `struct ocfs2_inode_handle` stores inode block number and generation.
- `ocfs2_encode_fh()` emits a 3-word handle for the inode: high 32 bits of block number, low 32 bits, generation.
- If a parent is supplied, it emits a 6-word connectable handle with parent block number and generation and returns type 2.

Handle decoding:
- `ocfs2_fh_to_dentry()` validates length/type, decodes the target handle, and calls `ocfs2_get_dentry()`.
- `ocfs2_fh_to_parent()` validates type 2 handles, decodes parent fields, and calls `ocfs2_get_dentry()`.

`ocfs2_get_dentry()` behavior:
- Rejects block number zero as stale.
- First checks `ocfs2_ilookup()` for an in-memory inode and validates generation.
- If not cached, takes the NFS sync lock in EX mode to serialize against inode deletion on all nodes.
- Checks the inode allocator bit with `ocfs2_test_inode_bit()` before calling `ocfs2_iget()`.
- Converts invalid inode-bit lookups into `-ESTALE` where appropriate.
- Rejects generation mismatch with `-ESTALE`.
- Returns an alias dentry via `d_obtain_alias()`.

`ocfs2_get_parent()` behavior:
- Takes the NFS sync lock and a PR inode metadata lock on the child directory inode.
- Looks up `".."` with `ocfs2_lookup_ino_from_name()`.
- Verifies the parent inode allocator bit before obtaining an alias for `ocfs2_iget()`.

Export operations:
- `encode_fh`
- `fh_to_dentry`
- `fh_to_parent`
- `get_parent`

Important invariants:
- Generation checks are mandatory to avoid resurrecting stale NFS handles after inode reuse.
- The NFS sync lock serializes export lookup against clustered inode deletion.
- Parent lookup relies on directory metadata locking and allocator-bit validation.
