# File Research: sources/os/linux/linux/fs/xfs/xfs_attr_inactive.c

Removes and invalidates an inode’s entire extended attribute fork during inode inactivation.

Key elements:
- `xfs_attr3_rmt_stale` maps remote attribute value extents and marks their incore buffers stale.
- `xfs_attr3_leaf_inactive` scans a leaf block, finds remote-value entries, and invalidates all remote value buffers.
- `xfs_attr3_node_inactive` recursively walks attribute btree nodes depth-first, invalidates child subtrees, invalidates child buffers, removes parent entries, and rolls transactions between children.
- `xfs_attr3_root_inactive` starts at attr block zero, handles node or leaf roots, reinitializes the root as an empty leaf before truncation, and rolls the transaction.
- `xfs_attr_inactive` allocates an attr-invalidation transaction, joins the inode, invalidates remote data and attr blocks, truncates all attr fork extents, invalidates the root block, removes the attr fork, and commits.

Dependencies:
- Uses attr leaf/node parsing, remote attr invalidation, bmap truncation, dir/attr health marking, and transaction roll helpers.
- Uses `xfs_attr_fork_remove` and `xfs_ifork_zap_attr` to remove on-disk and in-core fork state.

Research notes:
- The in-core attr fork is destroyed even on error.
- Remote attr value buffers are never logged, so stale marking is safe before extent removal.
- Tree recursion is bounded by `XFS_DA_NODE_MAXDEPTH`; excessive depth marks the attr fork sick and returns corruption.
- Reinitializing the root before truncating extents is a crash-safety measure to avoid entries pointing at freed remote blocks.
