# sources/sync-backup/casync/src/quota-projid.c

Purpose: reads and writes Linux filesystem project quota IDs on an open file descriptor.

Important APIs/types/functions: `read_quota_projid` uses `FS_IOC_FSGETXATTR` and returns `fsx_projid`; `write_quota_projid` reads existing `fsxattr`, changes only `fsx_projid`, and writes it back with `FS_IOC_FSSETXATTR`.

Control flow/state: functions are stateless wrappers around `ioctl`. `write_quota_projid` preserves all other extended inode flags by round-tripping the current struct first.

Dependencies/integration: depends on Linux `<linux/fs.h>` and open file descriptors from higher-level archive/extract code that wants quota project inheritance.

Risks/test signals: only works on filesystems supporting these ioctls; failures return negative errno. Race potential exists if another process changes fsxattr between get and set. Tests are likely platform-dependent and not direct in this subset.

Source research group: `subset-b-009122`.
