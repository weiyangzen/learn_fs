# File Research: sources/os/linux/linux/fs/omfs/dir.c

OMFS directory operations. Directories are hash tables stored in the directory inode block, with each bucket pointing to a linked list of inode blocks via `i_sibling`.

Main responsibilities:
- Hash names with a simple case-folding XOR hash and map them to fixed directory buckets.
- Lookup entries by reading the bucket head and scanning the sibling chain.
- Create files/directories by allocating a new inode, initializing its on-disk table, and linking it into the parent bucket.
- Delete entries by unlinking the target inode from its bucket chain.
- Implement readdir using `ctx->pos` split into high bits for bucket index and low bits for position inside a hash chain.
- Implement rename by deleting the old link first, then adding the inode under the new dentry name.
- Export OMFS directory inode and file operation tables.

Key functions:
- `omfs_get_bucket()` computes the bucket offset and reads the directory inode block.
- `omfs_scan_list()` follows a bucket chain and validates each inode block with `omfs_is_bad()`.
- `omfs_make_empty()` initializes an inode block as either a directory bucket table filled with `0xff` terminators or a file extent table.
- `omfs_add_link()` prepends the new inode to the target bucket and writes name, sibling, and parent fields to the child inode.
- `omfs_delete_entry()` removes a chain node by updating either the bucket head or the previous inode’s sibling pointer.
- `omfs_fill_chain()` emits directory entries while following a hash chain.
- `omfs_readdir()` emits dots, then iterates buckets and chains with resumable position encoding.

Operation tables:
- `omfs_dir_inops`: lookup, mkdir, rename, create, unlink, rmdir.
- `omfs_dir_operations`: generic read dir, shared iterate, generic llseek.

Important invariants and risks:
- Directory bucket entries use `~0ULL` as the end-of-chain sentinel.
- `omfs_is_bad()` validates that an inode block’s self pointer matches the expected block and lies in the legal inode/data block range.
- `omfs_lookup()` rejects names longer than `OMFS_NAMELEN`.
- Rename supports only `RENAME_NOREPLACE`; other flags return `-EINVAL`.
- `omfs_dir_is_empty()` is intended to detect any non-sentinel bucket, but the implementation dereferences `ptr` after the loop, which is risky when all buckets are sentinel values.
