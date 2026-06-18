# sources/user-network-fs/samba/source3/modules/wscript_build

## Purpose
This Waf build script declares Samba source3 module subsystems, VFS modules, related test binaries, generated sources, dependencies, conditional enablement, and static/dynamic module settings.

## Important APIs, Types, and Functions
It uses build helper calls such as `bld.SAMBA3_SUBSYSTEM`, `bld.SAMBA3_MODULE`, `bld.SAMBA3_BINARY`, `bld.SAMBA_GENERATOR`, `bld.SAMBA_SUBSYSTEM`, `bld.CONFIG_SET`, `bld.CONFIG_GET`, `bld.SAMBA3_IS_ENABLED_MODULE`, and `bld.SAMBA3_IS_STATIC_MODULE`. In this subset, key declarations include `VFS_VIRUSFILTER_UTILS`, `vfs_xattr_tdb`, `vfs_zfsacl`, `vfs_worm`, `vfs_virusfilter`, `vfs_vxfs`, and `vfs_widelinks`.

## Control Flow
The script is evaluated by Samba's build system. Subsystems are declared first, followed by a long list of VFS module targets. Conditional blocks generate NFSv4 xattr RPC sources only when `vfs_nfs4acl_xattr` is enabled and RPC headers are available. Module enablement is driven by configuration checks and module selection helpers; some test binaries are marked `for_selftest=True`.

## State and Persistence
The file does not store runtime state. It persists build graph metadata into Waf's configured build outputs. Module static/dynamic choices and generated files affect produced binaries and installed modules.

## Dependencies and Integration Points
It integrates source files with Samba libraries and external dependencies such as `acl`, `attr`, `sunacl`, `dbwrap`, `xattr_tdb`, `cephfs`, `gfapi`, `tevent`, `dbus-1`, `uring`, and `varlink`. The virusfilter module depends on `samba-util` and `VFS_VIRUSFILTER_UTILS`; VxFS is built from `lib_vxfs.c vfs_vxfs.c`; ZFS ACL depends on `NFS4_ACLS sunacl`.

## Risks
Incorrect dependency or enablement expressions can silently omit modules or build them without required helper subsystems. `VFS_VIRUSFILTER_UTILS` is enabled only if `vfs_virusfilter` is enabled, so any other consumer would need a build rule change. Generated RPC source paths are sensitive to out-of-tree build path handling, as reflected by the copy/rpcgen workaround.

## Test Signals
Build matrix tests should toggle the selected modules static/dynamic/enabled/disabled, run selftest binaries declared here, verify generated NFS4 xattr sources in out-of-tree builds, and confirm expected external dependency detection.
