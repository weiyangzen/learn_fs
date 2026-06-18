# File Research: sources/local-fs/ocfs2-tools/o2info/o2info.1.in

This manpage template documents `o2info`, its mounted-file ioctl mode, and its privileged device/libocfs2 mode. It explains options for cluster-coherent querying, filesystem features, volume info, mkfs reconstruction, free inode counts, free fragmentation, space usage, file stat, version, and help.

The note section states that mounted filesystem queries depend on OCFS2 info ioctls added in Linux 2.6.37. Examples show non-root querying through a file path and privileged device-style queries.

The documented behavior matches the CLI: options can be composed, `--freefrag` requires a chunk size in KB, and file-focused commands require a mounted object rather than a block device.
