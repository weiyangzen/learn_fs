# File Research: sources/os/linux/linux-stable/fs/vboxsf/super.c

Implements vboxsf filesystem registration, mount parsing, superblock creation, inode cache allocation, backing-device setup, and module lifetime. Mount options include `nls`, `uid`, `gid`, `ttl`, `dmode`, `fmode`, `dmask`, and `fmask`. `nls` cannot be changed during reconfigure.

`vboxsf_fill_super()` allocates `vboxsf_sbi`, loads optional NLS, allocates a BDI id, disables readahead/io pages, maps the requested shared-folder source through the host service, stats the root path, creates inode 0 as root, and installs vboxsf super/dentry operations. Cleanup unwinds map, BDI id, NLS, IDR, and private state.

`vboxsf_setup()` serializes one-time module setup: inode cache creation, VirtualBox guest-device connection, UTF-8 mode selection, and optional host symlink visibility. `vboxsf_parse_monolithic()` rejects old binary mount data. Reconfigure applies changed options to the root inode. Module init registers the `vboxsf` filesystem; exit unregisters, disconnects, flushes RCU inode frees, and destroys the inode cache.

The superblock uses anonymous backing storage (`kill_anon_super`) and returns statfs data from the host via `vboxsf_fsinfo()`.
