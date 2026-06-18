# sources/user-network-fs/mergerfs/tests/posix_parity.py

## Purpose
Provides the shared Python harness for mounting mergerfs, creating paired native paths, comparing calls, and manipulating runtime xattr options.

## Important APIs, Types, and Functions
Key helpers include `find_mergerfs()`, `find_fusermount()`, `mount_mergerfs()`, `unmount_mergerfs()`, the `mergerfs_mount()` context manager, `compare_calls()`, `compare_access()`, `touch()`, `cleanup_dir()`, `mergerfs_get_option()`, `mergerfs_set_option()`, `parse_allpaths()`, `mergerfs_branches()`, `underlying_path()`, `pair_paths()`, and `should_compare_inode()`.

## Control Flow
Tests enter `mergerfs_mount()`, which creates temporary branch directories under `tests/.test_tmp`, mounts mergerfs with default `defaults,use_ino,category.create=mfs` options, yields mount and branches, then unmounts and removes the tree. Comparison helpers execute mergerfs and native callables, normalize `OSError.errno`, optionally compare values, and return failure strings.

## State and Persistence Behavior
The harness creates transient test directories and mountpoints and changes live mergerfs options through `user.mergerfs.*` xattrs. It cleans temporary trees on context exit.

## Dependencies and Integration Points
Depends on Python stdlib, `ctypes` access syscall binding, the built or installed `mergerfs` binary, and `fusermount3` or `fusermount`. Every `TEST_*` script imports these helpers.

## Risks and Edge Cases
Missing binaries raise `RuntimeError` and tests convert that to skip code 77. Cleanup can mask unmount failures. Runtime option parsing assumes colon-separated branch entries and xattr control availability.

## Test Signals
The harness itself is exercised by all tests; direct checks should cover missing mergerfs, missing fusermount, mount option overrides, xattr get/set, branch parsing, and cleanup after failures.
