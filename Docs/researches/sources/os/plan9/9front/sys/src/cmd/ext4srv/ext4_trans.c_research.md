# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_trans.c

Thin transaction integration layer between generic ext4 metadata mutation code and the JBD journal implementation.

Key behavior:
- `ext4_trans_set_block_dirty` reconstructs an `ext4_block` wrapper from an `ext4_buf`; when a journal and current transaction exist, it records the block through `jbd_trans_set_block_dirty`, otherwise it marks the buffer dirty in the cache.
- `ext4_trans_block_get_noread` and `ext4_trans_block_get` currently delegate directly to the block cache get functions.
- `ext4_trans_try_revoke_block` adds a revoke to the current transaction when one is active; if journaling exists but no transaction is active, it flushes the LBA from cache instead.

Notable dependencies:
- Requires `ext4.h`, `ext4_fs.h`, and `ext4_journal.h`.
- Depends on `buf->bc->bdev->fs` being populated.

Research notes:
- The header comments mention a `jbd_trans_get_access` step, but this implementation does not have a separate get-access operation.
- The layer keeps most ext4 code independent from direct JBD calls for dirty marking and revocation.
