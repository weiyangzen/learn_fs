# File Research: sources/os/bsd/openbsd-src/sbin/clri/clri.c

UFS inode clearing utility.

It opens a filesystem device read/write, pledges `stdio`, searches known UFS superblock offsets, validates UFS1/UFS2 magic, block size, and UFS2 superblock location, then validates all requested inode numbers against the filesystem inode count. For modern inode formats it clears the filesystem clean flag and writes the superblock.

For each inode argument it locates the containing inode block, reads it, zeros the selected UFS1 or UFS2 inode, assigns a new random generation number with `arc4random()`, writes the block back, and fsyncs. This is a low-level repair tool intended for explicit operator use on damaged filesystems.
