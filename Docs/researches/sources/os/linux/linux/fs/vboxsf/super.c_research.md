# File Research: sources/os/linux/linux/fs/vboxsf/super.c

## Purpose
Implements vboxsf filesystem registration, fs_context parsing, mount setup, superblock initialization, inode cache management, statfs, reconfiguration, and module lifecycle.

## Main Functions
- Mount option handling:
  - `vboxsf_parse_param()`: parses `nls`, `uid`, `gid`, `ttl`, `dmode`, `fmode`, `dmask`, and `fmask`.
  - `vboxsf_parse_monolithic()`: rejects obsolete binary mount data and uses generic parsing otherwise.
- Mount/superblock:
  - `vboxsf_fill_super()`: allocates `vboxsf_sbi`, loads NLS, sets up backing device, maps host folder, stats root, initializes root inode/dentry, and fills superblock fields.
  - `vboxsf_get_tree()`: ensures VirtualBox shared-folder setup then calls `get_tree_nodev()`.
  - `vboxsf_reconfigure()`: applies changed options to root inode.
- Inode/super ops:
  - `vboxsf_inode_init_once()`, `vboxsf_alloc_inode()`, `vboxsf_free_inode()`: manage `vboxsf_inode` cache and IDR removal.
  - `vboxsf_put_super()`: unmaps host folder, frees bdi id, unloads NLS, flushes RCU inode frees, destroys IDR.
  - `vboxsf_statfs()`: queries host volume info and fills `kstatfs`.
- Module setup:
  - `vboxsf_setup()`: creates inode cache, connects to guest device, sets UTF-8 mode, optionally enables symlink visibility.
  - `vboxsf_init()` / `vboxsf_fini()`: register/unregister filesystem and disconnect/destroy cache at module exit.

## Important Design Points
- Source string names the host shared folder to map.
- Default NLS is `CONFIG_NLS_DEFAULT`; UTF-8 avoids loading an NLS table.
- Readahead and IO pages are disabled on the backing device.
- `follow_symlinks` module parameter controls whether host resolves symlinks or guest sees symlink objects.
- `vboxsf_setup()` is global, serialized, and done lazily on first mount.
- `statfs()` reports synthetic file counts because host info may not provide meaningful inode counts.

## Cross-File Relationships
- Calls host wrappers: `vboxsf_connect()`, `vboxsf_disconnect()`, `vboxsf_set_utf8()`, `vboxsf_set_symlinks()`, `vboxsf_map_folder()`, `vboxsf_unmap_folder()`, `vboxsf_fsinfo()`.
- Uses inode initialization and stat helpers from `utils.c`.
- Publishes `vboxsf_fs_type` with ops implemented across vboxsf files.

## Risks / Review Notes
- Error paths must unmap folder, unload NLS, free IDA ids, destroy IDR, and free `sbi` in the correct order.
- Old binary mount data is explicitly unsupported.
- Case-sensitivity query failure is non-fatal, defaulting to case-sensitive behavior.
