# sources/test-tools/crashmonkey/code/testing/test_get_log_ent_size.c

Purpose: older standalone test intended to clear logs, write a test file, fsync it, stop logging, and iterate log entries containing metadata plus data.

Important APIs/control flow: opens `/dev/hwm1`, opens `/mnt/snapshot/testing/test_file2`, clears/enables logging, writes `TEXT`, fsyncs, sleeps, disables logging, then calls `HWM_GET_LOG_ENT_SIZE` and `HWM_GET_LOG_ENT` in a loop to print operation flags and data.

State and persistence behavior: mutates a file under `/mnt/snapshot/testing`, relies on wrapper volatile logs, and reads entries until `ENODATA`.

Dependencies and integration: includes `disk_wrapper_ioctl.h`, but references ioctl names not defined in the current header. Assumes an inserted wrapper and mounted snapshot.

Risks: this file is stale relative to the current two-step `HWM_GET_LOG_META`/`HWM_GET_LOG_DATA` ABI. It also loops on `write()` incorrectly by assigning the return value to `written` instead of accumulating bytes, so partial writes can repeat from the wrong offset. It opens created files without an explicit mode argument despite `O_CREAT`, which is undefined/incorrect for POSIX `open()`.

Test signals: as written, compile failure is likely and is itself a compatibility signal. Updating it to the current ABI would make it a useful integration test for log payload extraction.
