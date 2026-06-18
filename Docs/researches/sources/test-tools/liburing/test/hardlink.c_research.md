<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/hardlink.c -->
## sources/test-tools/liburing/test/hardlink.c

Purpose: tests `IORING_OP_LINKAT` hardlink creation, symlink-follow behavior, and expected linkat errors.

Important APIs/types/functions: `do_linkat`, `files_linked_ok`, `io_uring_prep_linkat`, `io_uring_wait_cqes`, `AT_EMPTY_PATH`, `AT_SYMLINK_FOLLOW`, `stat`, and `unlinkat`.

Control flow: the test creates a target file, optionally links it through `AT_EMPTY_PATH` when running as root, creates a symlink, links target to a new name, verifies inode/link counts, links through the symlink with follow flag, then verifies expected `-EEXIST` and `-ENOENT` error cases.

State and persistence behavior: several fixed test pathnames are created and always unlinked in the cleanup path. Hardlink state is validated by device, inode, and `st_nlink`.

Dependencies and integration points: exercises raw linkat semantics through io_uring and filesystem metadata.

Risks: root-only `AT_EMPTY_PATH` coverage is skipped for non-root. Existing files with the same names would interfere.

Test signals: pass means io_uring linkat mirrors syscall hardlink behavior for success and error paths.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/hardlink.c -->
