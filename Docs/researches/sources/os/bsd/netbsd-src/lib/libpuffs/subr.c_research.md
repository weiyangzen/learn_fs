# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/subr.c

This file provides miscellaneous libpuffs helpers for dirents, no-op filesystem callbacks, generic vnode callbacks, statvfs initialization, vattr initialization/update, and vnode-type/mode/stat conversion.

`puffs_gendotdent` emits either `.` or `..` by calling `puffs_nextdent`. `puffs_nextdent` checks whether the supplied result buffer has enough room for an aligned dirent, fills file number, type, name length, name, and record length, advances the dirent pointer, and subtracts from the residual length.

`puffs_fsnop_unmount`, `puffs_fsnop_sync`, and `puffs_fsnop_statvfs` provide simple defaults. The statvfs default sets block/frsize/iosize to `DEV_BSIZE`, all counts to zero, and name max to `MAXNAMLEN`. `puffs_zerostatvfs` wraps that default. `puffs_genfs_node_getattr` copies attributes from a puffs node and `puffs_genfs_node_reclaim` frees a puffs node with `puffs_pn_put`.

`puffs_setvattr` copies only meaningful, non-`PUFFS_VNOVAL` fields from one vattr to another. `puffs_vattr_null` initializes a vattr to VNON/NOVAL style defaults while setting block size from page size and zeroing flags/generation/vaflags. `puffs_vtype2dt`, `puffs_mode2vt`, `puffs_stat2vattr`, and `puffs_addvtype2mode` bridge vnode types, dirent dtypes, mode bits, and `struct stat`.
