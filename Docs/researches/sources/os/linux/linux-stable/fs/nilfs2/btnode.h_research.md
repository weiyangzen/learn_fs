# File Research: sources/os/linux/linux-stable/fs/nilfs2/btnode.h

## Summary
Declares the NILFS B-tree node cache interface and the context object used for changing node cache keys.

## Main Contents
- `struct nilfs_btnode_chkey_ctxt`.
- Node-cache inode initialization and cache clearing APIs.
- Node buffer create, read-submit, delete, and change-key APIs.

## Important Details
`nilfs_btnode_chkey_ctxt` carries the old key, new key, current buffer, and optional newly allocated replacement buffer across prepare, commit, and abort phases.

## Risks
The header exposes a prepare/commit/abort protocol; callers must keep the context intact and complete the protocol to avoid stale xarray entries or leaked temporary buffers.
