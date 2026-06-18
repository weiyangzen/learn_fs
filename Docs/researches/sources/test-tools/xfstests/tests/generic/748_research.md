# sources/test-tools/xfstests/tests/generic/748


Purpose: Regression loop for a Btrfs fsync crash involving preallocation beyond i_size, xattr updates, direct writes that extend i_size, and fdatasync/logging races.


Important APIs, helpers, and commands: Uses `common/attr`, `_require_attrs`, `_require_odirect`, `_require_xfs_io_command falloc -k`, `SETFATTR_PROG`, and `XFS_IO_PROG` with `-ftd`/`-d` command sequences.
 It imports `./common/attr`, `./common/preamble`.
 Capability gates include `_require_attrs`, `_require_odirect`, `_require_scratch`, `_require_xfs_io_command`.
 Regression annotations include `_fixed_by_fs_commit btrfs 9d274c19a71b \`.



Control flow, state, dependencies, risks, and test signals: After mkfs/mount it removes `-i` from `XFS_IO_PROG` to make startup faster, obtains the block size, and repeats 5000 falloc/write/xattr/direct-write cycles against one file. State is the scratch file, its prealloc extents, xattrs, ordered extents, and filesystem log state. It depends on xfs_io fallocate/direct write support and user xattrs. Risks are race sensitivity, long loop cost, and filesystem-specific behavior outside Btrfs. The only expected signal is no crash and `Silence is golden`. Source size is 44 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
