<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime07.c

Purpose: verifies `utime()` follows symbolic links for timestamp updates and reports correct errors for dangling and self-referential symlinks.

Important APIs/types/functions: `create_symlink()` wraps `SAFE_SYMLINK()` and verifies `S_IFLNK` with `SAFE_LSTAT()`. `test_utime()` symlinks to the tmpdir and expects target atime/mtime deltas of `TIME_DIFF`; `test_utime_no_path()` expects `ENOENT`; `test_utime_loop()` expects `ELOOP`.

Control flow/state: `run()` executes three independent subtests, each creating and unlinking its own symlink. The positive case uses `SAFE_STAT()` rather than `lstat()`, intentionally checking the target path after symlink resolution.

Dependencies/integration: uses only an LTP tmpdir and standard symlink support; no root or mount matrix is required.

Risks/test signals: exact timestamp-delta checks can be sensitive to filesystem timestamp resolution. Error cases are strong signals for path resolution behavior: dangling target must not be created, and a symlink loop must fail with `ELOOP`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime07.c -->
