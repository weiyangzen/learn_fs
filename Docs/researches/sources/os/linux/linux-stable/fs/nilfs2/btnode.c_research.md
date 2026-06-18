# File Research: sources/os/linux/linux-stable/fs/nilfs2/btnode.c

## Summary
Implements the page-cache backed B-tree node cache used by NILFS block maps. It creates, reads, deletes, and relocates cached B-tree node buffers, including support for virtual block number translation through DAT.

## Main Responsibilities
- Initializes the special inode used as a B-tree node cache.
- Clears cached node pages.
- Creates new node buffers at logical cache keys.
- Submits node block reads with optional sibling readahead.
- Invalidates deleted node buffers.
- Prepares, commits, or aborts node cache key changes when node block numbers change.

## Important Behavior
`nilfs_init_btnc_inode()` configures an associated regular inode with `nilfs_buffer_cache_aops` and `GFP_NOFS` allocation. `nilfs_btnode_create_block()` grabs a buffer, rejects already-used buffers as metadata inconsistency, zeros it, marks it mapped and uptodate, and returns it with the folio released.

`nilfs_btnode_submit_block()` uses cache block numbers as lookup keys, translates virtual block numbers through DAT for non-DAT metadata files, and temporarily sets `b_blocknr` to the physical address for I/O before restoring the cache key. Readahead only proceeds for sequential physical blocks and uses `-EEXIST` and `-EBUSY` as internal status codes.

The change-key path supports two modes. When block size equals page size, it inserts the existing folio into the xarray at the new key and later moves the folio index. Otherwise it allocates a replacement buffer, copies data and flags, then deletes the old buffer. Abort reverses either the xarray insertion or the temporary replacement buffer.

## Risks
Key-change logic relies on folio locking and assumes no folio size larger than page size. Duplicate cached block use is treated as corruption. Callers must interpret internal `-EEXIST` and `-EBUSY` statuses correctly and must call commit or abort after successful prepare.
