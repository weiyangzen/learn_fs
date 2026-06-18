# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/find_block_inode.c

## Role

`find_block_inode.c` implements the `icheck` backend: given one or more physical block numbers, it tries to identify the inode or allocator metadata that owns each block.

## Algorithm

It initializes a block-status array, locates the global bitmap inode, marks computed reserved blocks such as the superblock zone and group descriptor zones, scans the bitmap to classify free blocks, then scans all inodes.

For valid inodes in the current filesystem generation, it checks whether the queried block is the inode block itself, a chain allocator group descriptor, an extent block, or a data block within a leaf extent. For regular data blocks it records the logical block offset.

## Output

It delegates final rows to `dump_icheck()`, reporting used/free/unknown status, owning inode, and optional data offset.

## Risk Areas

The scan is exhaustive and can be expensive on large filesystems. It ignores invalid-generation or non-valid inodes and treats some metadata ownership through computed layout rules rather than direct reverse references.
