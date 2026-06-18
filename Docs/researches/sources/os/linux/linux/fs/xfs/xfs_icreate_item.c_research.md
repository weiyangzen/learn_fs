# File Research: sources/os/linux/linux/fs/xfs/xfs_icreate_item.c

Implements the XFS inode-create log item used to log initialization of newly allocated inode chunks and replay them during recovery.

Key elements:
- Defines the global `xfs_icreate_cache` slab cache and `ICR_ITEM` helper.
- Log item ops compute size, format a single `xfs_icreate_log` vector, and release cache/shadow memory after commit.
- `xfs_icreate_log` allocates an icreate item, fills AG/block/count/inode-size/length/generation fields in big-endian log format, joins it to the transaction, marks the transaction dirty, and sets the item dirty bit.
- Recovery reorder places icreate replay with buffer-list replay because inode items modifying the same buffers must see initialized inode cluster buffers first.
- Recovery pass validates log item type/size, AG/block/count/inode-size/length consistency, supported sparse/full chunk lengths, and count-vs-length geometry.
- Recovery checks for canceled inode cluster buffers and skips replay if the chunk was canceled.
- Successful replay calls `xfs_ialloc_inode_init` to stamp inode templates into delayed-write buffers.

Dependencies:
- Integrates with XFS transaction/log item infrastructure, log recovery, inode allocation geometry, buffer cancellation tracking, and tracing.

Research notes:
- Recovery currently expects all or none of the inode cluster buffers in a logged allocation to be canceled; partial cancellation only warns and skips replay.
- The item acts as the logical equivalent of logging newly initialized inode buffers without logging every byte of the chunk.
