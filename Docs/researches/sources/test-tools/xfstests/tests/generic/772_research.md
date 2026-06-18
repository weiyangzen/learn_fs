# sources/test-tools/xfstests/tests/generic/772


Purpose: Tests VFS file attribute get/set behavior for FS_XFLAG_NODUMP on directories, special files, sockets, and symlinks including broken symlink no-follow handling.


Important APIs, helpers, and commands: Uses `file_getattr`, `file_setattr`, `file_attr`, `_filter_vfs_file_attributes`, `_require_file_attr`, `_require_mknod`, and symlink support.
 Local helper functions detected in the file include `file_attr`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_file_attr`, `_require_mknod`, `_require_scratch`, `_require_symlinks`, `_require_test_program`.



Control flow, state, dependencies, risks, and test signals: It creates a project directory with fifo, char/block devices, socket, symlink, and broken symlink, reads initial attributes, sets nodump on each, reads back filtered attributes, then compares follow vs no-follow behavior for broken symlinks. State is inode flag metadata on heterogeneous file types. Dependencies are file attribute test helper, mknod, socket creation, and symlink support. Risks are privilege requirements for device nodes and filesystem flag support differences. Signals are normalized attribute output. Source size is 75 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
