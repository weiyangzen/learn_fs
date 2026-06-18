# sources/user-network-fs/pyfuse3/test/test_examples.py

Purpose: End-to-end tests for pyfuse3 example filesystems and common filesystem operations through mounted FUSE instances.

Important APIs/types/functions: Test entry points `test_hello`, `test_tmpfs`, and `test_passthroughfs`. Helper operations include `checked_unlink`, `tst_mkdir`, `tst_symlink`, `tst_mknod`, `tst_chown`, `tst_chmod`, `tst_write`, `tst_unlink`, `tst_statvfs`, `tst_link`, `tst_rename`, `tst_readdir`, `tst_truncate_path`, `tst_truncate_fd`, `tst_utimens`, `tst_rounding`, `tst_passthrough`, and `assert_same_stats`.

Control flow: Tests spawn example scripts as subprocesses, wait for mount readiness, perform host filesystem syscalls against the mount, and unmount/cleanup. The passthrough test checks both source-to-mount and mount-to-source propagation. Rounding tests set nanosecond timestamps near a precision boundary.

State and persistence: Uses pytest temporary directories as mountpoints and backing directories. Subprocess mounts are cleaned via utility helpers. A global `name_generator` creates unique names within the process.

Dependencies and integration points: Depends on FUSE availability, pyfuse3 examples, `fusermount`/`umount`, host permissions, and external OS semantics for links, ownership, chmod, utime, truncation, and statvfs.

Risks: FUSE mounts can hang or leave stale mountpoints if cleanup fails. Chown tests are skipped for passthrough unless root. Timestamp equality has CI exceptions for known libfuse/kernel precision behavior.

Test signals: This is the primary behavior signal for `examples/tmpfs.py`, passthroughfs, hello examples, writeback-cache behavior, and pyfuse3's syscall mapping.
