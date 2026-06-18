# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zut/zut.c

This file implements the ZFS unit-test pseudo driver `/dev/zut`. The driver exposes ioctl helpers used to exercise vnode lookup, extended attribute lookup, readdir, case-insensitive lookup behavior, directory-entry flags, access filtering, and extended stat attributes from kernel context.

`zut_open_dir()` resolves a directory path from either root or the caller’s current directory, using the process root/current directory under `p_lock`, `lookuppnvp()`, and a final directory read-access check. It handles ACE-aware filesystems with `ACE_LIST_DIRECTORY` and falls back to `VREAD` otherwise.

`zut_readdir()` copies in a `zut_readdir_t`, opens the requested directory, optionally switches to a named-attribute directory by looking up a file and then `LOOKUP_XATTR`, builds a kernel `uio`, maps request flags to `V_RDDIR_ENTFLAGS` and `V_RDDIR_ACCFILTER`, calls `VOP_READDIR()` under a vnode read lock, copies directory data and updated metadata back to userland, and releases all vnodes. `zut_lookup()` similarly resolves a directory, optionally enables `FIGNORECASE`, looks up a file or named attribute file, optionally fills a stat buffer via `zut_stat64()`, and returns the resolved path and directory-entry flags.

`zut_stat64()` requests normal stat attributes plus a set of ZFS/system extended attributes through `xvattr_t`. It fills a `stat64` and translates returned xoptattr bits into `F_ARCHIVE`, `F_SYSTEM`, `F_READONLY`, `F_HIDDEN`, `F_NOUNLINK`, `F_IMMUTABLE`, `F_APPENDONLY`, `F_NODUMP`, `F_OPAQUE`, AV flags, reparse, offline, and sparse bits.

The driver shell is a single minor pseudo device. `zut_ioctl()` accepts `ZUT_IOC_LOOKUP` and `ZUT_IOC_READDIR` after command-range and minor checks. `zut_attach()` creates the `"zut"` character minor node, `zut_detach()` removes properties and minors, and `zut_info()`, `zut_open()`, and `zut_close()` implement standard pseudo-driver plumbing. `_init()` installs the module and obtains an LDI identifier; `_fini()` removes it and releases that identifier.

The main dependencies are vnode lookup/read/stat operations, pathname handling, ACE/VREAD access checks, DDI pseudo-device registration, and structures from `sys/fs/zut.h`. The ioctl path is intentionally narrow but must carefully release vnodes on all lookup branches and preserve user/kernel copyout semantics.
