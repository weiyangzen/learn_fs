# File Research: sources/local-fs/ntfs-3g/ntfsprogs/cluster.h

Header for cluster ownership search helpers. It includes NTFS `types.h` and `volume.h`, declares a placeholder `ntfs_cluster` struct, defines the `cluster_cb` callback type, and declares `cluster_find()`.

The callback contract is `int (cluster_cb)(ntfs_inode *ino, ATTR_RECORD *attr, runlist_element *run, void *data)`, letting callers inspect the owning inode, owning attribute record, and overlapping run. This header depends on libntfs volume/inode/attribute/runlist types being visible through the included headers.
