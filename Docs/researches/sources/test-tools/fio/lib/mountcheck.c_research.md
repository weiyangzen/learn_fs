# sources/test-tools/fio/lib/mountcheck.c

Purpose: portability helper to detect whether a device path is currently mounted.

Important APIs/functions: `device_is_mounted(const char *dev)`. The implementation has compile-time branches for `getmntent`, BSD `getmntinfo` with `statfs`, NetBSD `statvfs`, and a default unsupported path returning 0.

Control flow: supported branches enumerate mount table entries and compare the mount source name with `dev`, returning 1 on exact match and 0 otherwise.

State/persistence: no persistent state. The `getmntent` branch opens `/etc/mtab` and closes it with `endmntent`.

Dependencies/integration: selected by configure macros and OS headers. Used by fio safety checks around devices/files.

Risks/test signals: exact string matching may miss symlinks, canonicalized paths, bind mounts, or systems where `/etc/mtab` is stale. Tests should use temporary mounts or mocked platform calls where possible and verify unsupported builds fail closed as "not mounted".
