# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/ebh_misc.h

This header provides small EBH utility macros.

Key macros:
- `CHFS_GET_MEMBER_POS(type, member)`: computes member offset using a null pointer expression.
- `CHFS_GET_LID(lid)`: converts a little-endian LID to host order and masks off the NOR dirty bit.
- `EBH_TREE_DESTROY`: removes and frees every node in an RB tree.
- `EBH_TREE_DESTROY_MUTEX`: same as `EBH_TREE_DESTROY`, but also destroys each node’s rwlock.
- `EBH_QUEUE_DESTROY`: removes and frees every node in a TAILQ.

Dependencies:
- Kernel RB tree, TAILQ, `kmem_free`, and for the mutex variant, `rw_destroy`.
- `CHFS_GET_LID` depends on `CHFS_LID_DIRTY_BIT_MASK` from `ebh_media.h`.

Design notes:
- These macros are destructive and assume exclusive ownership of the tree/queue.
- The mutex destroy macro is marked as a hack, reflecting that lock lifetime is embedded in RB-tree node lifetime.
