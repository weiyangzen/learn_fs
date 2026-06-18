<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime03.c

Purpose: verifies an unprivileged non-owner with write permission can call `utime(path, NULL)` to set atime and mtime to current time.

Important APIs/types/functions: `setup()` selects two non-root UIDs using `SAFE_GETPWNAM("nobody")` and `tst_get_uids()`, creates `mntpoint/tmp_file` with mode `0766`, and chowns it to `nobody`. `run()` establishes initial explicit timestamps, switches euid to the second user, calls `utime(NULL)`, restores root euid, and validates the timestamps.

Control flow/state: the key branch is credential switching around the `utime()` call. The file remains owned by `nobody`, while the caller is a different user that relies on write access.

Dependencies/integration: depends on LTP UID discovery and mounted filesystem timestamp helpers. It is root-only because it changes ownership and effective UID.

Risks/test signals: meaningful failures are `utime()` permission denial or atime/mtime outside the measured window. Systems with insufficient distinct test UIDs or unusual ownership semantics can fail setup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime03.c -->
