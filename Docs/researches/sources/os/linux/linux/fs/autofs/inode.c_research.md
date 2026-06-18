# File Research: sources/os/linux/linux/fs/autofs/inode.c

## Summary
Handles autofs superblock setup, mount option parsing, inode allocation, and superblock teardown.

## Main Responsibilities
- Allocate and clean `autofs_info` objects.
- Allocate and initialize `autofs_sb_info`.
- Parse fs_context mount parameters including daemon pipe fd, uid/gid, pgrp, protocol versions, type, strict expire, and ignore.
- Validate daemon/kernel protocol compatibility.
- Fill the superblock root inode/dentry.
- Expose mount options through `show_options`.
- Tear down autofs state and enter catatonic mode on kill.

## Key APIs
- `autofs_init_fs_context()`.
- `autofs_get_inode()`.
- `autofs_kill_sb()`.
- `autofs_new_ino()`, `autofs_clean_ino()`, `autofs_free_ino()`.
- `autofs_param_specs`.

## Important Behavior
The pipe fd is opened during parameter parsing so it is resolved in the original syscall context. The pipe must be a writable FIFO and is forced into packet-pipe mode.

New superblocks start catatonic and become active only after root setup and daemon process group selection. Direct or offset trigger roots are marked managed so VFS path walk invokes autofs.

Protocol validation chooses the highest supported version within daemon-supplied min/max bounds and sets protocol subversions for v4/v5.

## Risks
`autofs_fill_super()` must release partially allocated root state on failures; one path after `autofs_get_inode()` failure returns without freeing the newly allocated `autofs_info`. Mount parsing and pipe ownership are sensitive because daemon communication depends on a valid writable packet FIFO.
