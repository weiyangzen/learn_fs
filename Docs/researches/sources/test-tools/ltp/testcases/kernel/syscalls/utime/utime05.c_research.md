<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime05.c

Purpose: verifies an unprivileged owner can set explicit atime and mtime with `utime(path, &times)`.

Important APIs/types/functions: `setup()` chmods the mount point to `0777`, switches euid to `nobody`, and creates `mntpoint/tmp_file`; `times` holds fixed values `20000` and `10000`. `run()` calls `utime()` and validates both stat fields.

Control flow/state: after root prepares a writable mount point, all file creation and timestamp mutation happen as `nobody`. The test checks ownership-based permission rather than privilege.

Dependencies/integration: uses LTP safe account lookup, euid switching, mounted filesystem orchestration, and skips `vfat`/`exfat`.

Risks/test signals: the primary risks are mountpoint permission setup and filesystems that do not preserve exact test timestamps. Runtime failures directly indicate `utime()` permission or timestamp-setting regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime05.c -->
