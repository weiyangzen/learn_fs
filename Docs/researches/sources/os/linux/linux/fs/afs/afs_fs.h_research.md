# File Research: sources/os/linux/linux/fs/afs/afs_fs.h

Purpose: defines AFS file service port, service ID, operation IDs, and file-service abort/error codes.

Key contents:
- `AFS_FS_PORT = 7000`, `FS_SERVICE = 1`.
- File service ops include fetch/store data, ACL/status, create/remove/rename/symlink/link/mkdir/rmdir, callback give-up, volume info/status, bulk status, locks, lookup, 64-bit data ops, capabilities.
- Error codes include volume restart/salvage/not found/offline/busy/moved/I/O/quota/full/restricted states.

Implementation notes:
- Operation IDs are consumed by fsclient/yfsclient operation descriptors elsewhere and referenced by callback/security code.
- Error constants are translated into Linux errors in higher-level operation handling.
