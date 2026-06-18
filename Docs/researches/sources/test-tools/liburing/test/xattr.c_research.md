# sources/test-tools/liburing/test/xattr.c

Purpose: verifies io_uring extended attribute operations for both fd-based and path-based APIs, including success paths and invalid argument behavior.

Important APIs/types/functions: wrappers `io_uring_fsetxattr`, `io_uring_fgetxattr`, `io_uring_setxattr`, `io_uring_getxattr`; tests `test_fxattr`, `test_xattr`, `test_failure_fxattr`, `test_failure_xattr`, `test_invalid_sqe`; liburing prep helpers `io_uring_prep_fsetxattr`, `io_uring_prep_fgetxattr`, `io_uring_prep_setxattr`, and `io_uring_prep_getxattr`.

Control flow: main runs fd-based set/get first. `test_fxattr` creates `xattr.test`, writes two `user.*` attributes, and reads them back by fd. If the first set reports `-EINVAL` or `-EOPNOTSUPP`, `no_xattr` is set and the rest of the test exits successfully. Otherwise path-based set/get does the same using a filename. Failure tests then submit bad fd/path/name/value/size combinations and require failures or zero-length success where appropriate. A destructive invalid-SQE case is compiled only under `DESTRUCTIVE_TEST`.

State/persistence behavior: creates and unlinks `xattr.test` in multiple tests. Attribute state is written to the file and checked before cleanup.

Dependencies/integration: requires filesystem support for `user.*` xattrs, kernel io_uring xattr op support, and normal VFS xattr permission behavior.

Risks/test signals: skips xattr-op unsupported kernels by exiting success after fd test. Some invalid cases rely on kernel validation order and on zero-size xattr semantics. Failures are wrong CQE status, wrong returned value length, or mismatched value bytes.
