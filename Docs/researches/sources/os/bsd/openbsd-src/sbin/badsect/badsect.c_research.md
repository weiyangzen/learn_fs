# File Research: sources/os/bsd/openbsd-src/sbin/badsect/badsect.c

Legacy UFS bad-sector containment utility.

Given a bad-block directory and filesystem-relative sector numbers, it locates the mounted filesystem’s block device by scanning `/dev`, rewrites the path to the raw character device, reads the UFS superblock and cylinder group metadata, checks whether each requested filesystem block is in range and in a data area, warns if the sector is already allocated, then creates special files named after the sectors using `mknod()` with the filesystem block number as device data.

It reads disk metadata with `pread()` and exits nonzero on read, stat, open, or metadata validation failures. After creating containment nodes it reminds the operator to run `fsck` on the raw device.
