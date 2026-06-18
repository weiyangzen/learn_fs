# File Research: sources/os/linux/linux/fs/orangefs/orangefs-debug.h

Defines OrangeFS debug mask bits used by gossip logging.

The file assigns one bit per subsystem (`super`, `inode`, `file`, `dir`, `utils`, `wait`, `acl`, `dcache`, `dev`, `name`, `bufmap`, `cache`, `debugfs`, `xattr`, `init`, `sysfs`) plus `none`, `all`, and max-mask constants. It is shared with kernel and non-kernel builds.
