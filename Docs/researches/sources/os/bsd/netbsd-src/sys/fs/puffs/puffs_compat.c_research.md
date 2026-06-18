# File Research: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_compat.c

This file provides PUFFS protocol compatibility translation for older 5.0-style userland, primarily covering 32-bit `time_t` and narrower `dev_t` layout differences. It defines local compatibility structures (`vattr50`, `puffs50_vfsmsg_fhtonode`, and selected `puffs50_vnmsg_*` messages) matching older wire formats.

The core conversion helpers are `vattr_to_50()` and `vattr_from_50()`, translating `struct vattr` time fields through `timespec_to_timespec50()`/`timespec50_to_timespec()` and narrowing/widening fields such as `va_fsid` and `va_rdev`. `puffs_compat_outgoing()` conditionally allocates a translated request for operations whose message layout changed: `VFS_FHTOVP`, `VN_LOOKUP`, `VN_CREATE`, `VN_MKNOD`, `VN_MKDIR`, `VN_SYMLINK`, `VN_SETATTR`, and `VN_GETATTR`. It returns both the compatibility request and the size delta so `puffs_msg_enqueue()` can send the older layout while retaining the original request for incoming conversion.

`puffs_compat_incoming()` reverses selected reply fields into the original modern request. For create-like operations it primarily copies the new node cookie; for lookup/fhtovp it also copies type, size, and rdev; for getattr it translates `vattr50` back to modern `vattr`.

`puffs_50_init()` and `puffs_50_fini()` register/unregister the conversion callbacks through module hooks (`puffs_out_50_hook`, `puffs_in_50_hook`). This file is tightly coupled to `puffs_msgif.c`, which invokes the hooks when `pmp_docompat` is set from mount arguments.
