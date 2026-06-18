# File Research: sources/os/linux/linux/fs/ntfs/index.h

## Purpose
Defines the NTFS index context structure and declares the public index manipulation and traversal APIs.

## Key Elements
`struct ntfs_index_context` records the target index inode/name, current entry, entry data pointer/length, root-vs-allocation location, resident root context, current index block, opened index allocation inode, parent VCN/position stacks, dirty state, index block size, VCN shift, and sync-write flag. Constants define the synthetic root parent VCN and maximum traversal depth.

## Dependencies And Integration
Includes Linux `fs.h` plus NTFS attribute and MFT headers. Public functions are consumed by directory operations, namespace operations, inode synchronization, and xattr code that needs index-backed metadata.

## Behavior/Risks
The context owns borrowed pointers into mapped MFT records or allocated index blocks, so callers must release it with `ntfs_index_ctx_put()` after using `entry` or `data`. If callers modify an entry, they must mark it dirty or synchronously write it before releasing the context.
