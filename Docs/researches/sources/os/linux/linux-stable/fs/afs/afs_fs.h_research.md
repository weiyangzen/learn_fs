# File Research: sources/os/linux/linux-stable/fs/afs/afs_fs.h

This header defines AFS file-service port, service ID, file-service RPC operation numbers, and AFS file-service abort/error codes.

Major contents:
- Defines `AFS_FS_PORT` as 7000 and `FS_SERVICE` as 1.
- Enumerates classic file-service operations including fetch/store data, fetch/store ACL, fetch/store status, remove, create, rename, symlink, link, mkdir, rmdir, callback release, volume info/status, root volume, bulk status, locks, and lookup.
- Enumerates extended operation IDs such as inline bulk status, 64-bit fetch/store data, give-up-all-callbacks, and get-capabilities.
- Defines volume/file service abort codes such as `VNOVNODE`, `VNOVOL`, `VOFFLINE`, `VDISKFULL`, `VOVERQUOTA`, `VMOVED`, `VIO`, and `VSALVAGING`.

Usage:
- Directory operations use these constants indirectly through AFS/YFS operation dispatch tables.
- Callback and security paths check `FS_SERVICE` when routing challenges and callback-related appdata.
- Remote deletion detection maps aborts like `VNOVNODE` into local vnode deletion state.
