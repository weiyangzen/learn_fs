# sources/test-tools/crashmonkey/code/tests/generic_066.cpp

Purpose: btrfs generic/066 xattr deletion regression. It creates three user xattrs, removes the second, fsyncs the file, and checks the deleted xattr does not reappear after recovery.

Important APIs/types/functions: `Generic066`, `fsetxattr`, `removexattr`, `getxattr`, `fsync`, `Checkpoint`, conditional xattr include, and `DataTestResult::kFileMetadataCorrupted`.

Control flow: `setup()` creates `foo`, sets `user.xattr1`, `user.xattr2`, and `user.xattr3`, syncs, and closes. `run()` removes `user.xattr2`, fsyncs `foo`, and checkpoints. `check_test()` attempts to read `user.xattr2`; if it is still present with `val2` after checkpoint 1, it reports corruption.

State/persistence behavior: xattr deletion must be durably logged by file fsync, while other attrs are not explicitly checked.

Dependencies/integration: requires user xattr support and proper include path selection for kernel/libc versions.

Risks/test signals: only the removed xattr is checked; loss of xattr1/xattr3 would not be detected. Signal is deleted xattr resurrection.
