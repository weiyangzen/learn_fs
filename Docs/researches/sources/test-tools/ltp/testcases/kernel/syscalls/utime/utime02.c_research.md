<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime02.c

Purpose: verifies an unprivileged effective user can call `utime(path, NULL)` on a file that it owns, even when the file mode is read-only.

Important APIs/types/functions: `setup()` gets `nobody`, creates `mntpoint/tmp_file`, chowns it to that UID/GID, then switches effective UID. `run()` uses explicit `utimbuf` setup followed by the `NULL` timestamp update, `SAFE_STAT()`, and LTP timestamp bounds.

Control flow/state: after ownership and euid setup, the test confirms explicit atime/mtime assignment works, then verifies `NULL` updates both times to current filesystem time. State changes are confined to ownership and timestamps of the temporary file.

Dependencies/integration: requires root to prepare ownership and switch credentials, plus the LTP mounted filesystem matrix. It skips `vfat`/`exfat` where ownership/timestamp semantics do not match the test.

Risks/test signals: failures distinguish permission errors from timestamp-range errors. A missing `nobody` account or unusual UID mapping would break setup rather than the syscall assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime02.c -->
