# sources/test-tools/xfstests/tests/generic/780


Purpose: Extends file attribute nodump testing to special files and symlinks, including no-follow behavior.


Important APIs, helpers, and commands: Uses `file_attr`, `_require_file_attr_special`, `_require_mknod`, `_filter_vfs_file_attributes`, AF_UNIX socket helper, and symlink support.
 Local helper functions detected in the file include `create_af_unix`, `file_attr`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_file_attr`, `_require_file_attr_special`, `_require_mknod`, `_require_scratch`, `_require_symlinks`, `_require_test_program`.



Control flow, state, dependencies, risks, and test signals: It creates a directory with fifo, char/block device, socket, symlink, and broken symlink, reads attributes, sets nodump across all, and verifies follow/no-follow semantics. State is VFS inode flags on special inode types. Dependencies are helper binaries, mknod permissions, and filesystem file-attribute support. Risks are special-file creation permissions and filesystems that reject flags on some inode types. Signals are normalized attribute listings. Source size is 86 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
