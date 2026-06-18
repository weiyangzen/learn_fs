# File Research: sources/teaching/minix/minix/fs/mfs/mount.c

`mount.c` handles mounting, mountpoint marking, and unmounting for the single-device MFS service instance. `fs_mount` stores `fs_dev`, opens the block device read-only or read-write, reads and validates the superblock, and remounts read-only if the filesystem is unclean and the caller requested writable access.

After `read_super`, it sets the libminixfs block size, computes `used_zones` by counting free zone bits, reports block usage to libminixfs, loads the root inode, fills the fsdriver root-node response, and marks the filesystem dirty on disk when mounted read-write.

`fs_mountpt` checks that the target inode is not already a mountpoint and not a special device node, then marks it as a mountpoint. `fs_unmount` checks for unexpected live inode references, releases the root inode, syncs inodes and buffers, marks a writable filesystem clean, closes the block device, invalidates cached blocks for the device, and clears `superblock.s_dev`.
