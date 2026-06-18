# File Research: sources/os/linux/linux/fs/9p/fid.c

Implements 9p FID lookup, attachment, cloning, and tracking on dentries and inodes.

Key behavior:
- Stores per-dentry FIDs in `dentry->d_fsdata` and open inode FIDs in `inode->i_private`, both as hlist heads.
- `v9fs_fid_add()` attaches a FID to a dentry and NULLs the caller’s pointer to transfer ownership.
- `v9fs_open_fid_add()` attaches an open FID to an inode and NULLs the caller’s pointer.
- `v9fs_fid_find_inode()` searches open inode FIDs by uid and optional writability.
- `v9fs_fid_find()` searches dentry FIDs first, then falls back to open inode FIDs.
- `build_path_from_dentry()` builds a root-relative component array while rename protection is held.
- `v9fs_fid_lookup_with_uid()` is the core lookup path:
  - Reuses a matching dentry/inode FID if present.
  - Walks from a parent FID when possible.
  - Attaches the user to the root if needed.
  - Walks from root in chunks capped by `P9_MAXWELEM`.
  - Adds the resulting FID back to the dentry if the dentry is still hashed.
- `v9fs_fid_lookup()` chooses uid matching policy based on access mode:
  - `access=single`, `user`, and `client` use `current_fsuid()`.
  - `access=any` permits any dentry FID and uses session uid.

Important interactions:
- Uses `v9ses->rename_sem` to stabilize path component names during walks.
- 9p mount access mode controls whether FIDs are per-user or shared.
- Dentry release in `vfs_dentry.c` is responsible for dropping dentry-held FIDs.
