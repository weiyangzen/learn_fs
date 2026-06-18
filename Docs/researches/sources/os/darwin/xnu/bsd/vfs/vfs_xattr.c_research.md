# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_xattr.c

## Purpose

`vfs_xattr.c` implements Darwin VFS extended attribute wrappers and default fallback support. It mediates native filesystem xattr VNOPs through security/name validation, supports named streams/resource forks, manages shadow stream files for filesystems without native named streams, and uses AppleDouble sidecar files plus `doubleagentd` for default non-native extended attributes when `CONFIG_APPLEDOUBLE` is enabled.

## APIs and Entry Points

- Public xattr wrappers: `vn_getxattr()`, `vn_setxattr()`, `vn_removexattr()`, `vn_listxattr()`.
- Name helpers: `xattr_validatename()`, `xattr_protected()`.
- Named stream APIs: `vnode_setasnamedstream()`, `vnode_getnamedstream()`, `vnode_makenamedstream()`, `vnode_removenamedstream()`, `vnode_relenamedstream()`, `vnode_flushnamedstream()`, `vnode_verifynamedstream()`.
- Shadow-stream internals: `vnode_setasnamedstream_internal()`, `getshadowfile()`, `default_getnamedstream()`, `default_makenamedstream()`, `default_removenamedstream()`, `is_shadow_dir_valid()`, `get_shadow_dir()`.
- AppleDouble fallback wrappers: `default_getxattr()`, `default_setxattr()`, `default_removexattr()`, `default_listxattr()`.
- DoubleAgent integration: `get_doubleagentd_port()`, `default_getxattr_doubleagent()`, `default_setxattr_doubleagent()`, `default_listxattr_doubleagent()`, `default_removexattr_doubleagent()`.
- Sidecar file helpers: `open_xattrfile()`, `close_xattrfile()`, `remove_xattrfile()`, `make_xattrfile_port()`.

## Control Flow

The public `vn_*xattr()` functions first reject unsupported vnodes and named-stream vnodes where direct xattr calls are invalid. User-originated operations validate UTF-8 names, run MACF checks when configured, and authorize the appropriate `KAUTH_VNODE_*_EXTATTRIBUTES` right. Resource fork xattrs are special: they may use nonzero `uio` offsets, while other attributes reject nonzero offsets.

Each public operation first calls the filesystem native VNOP. On `ENOTSUP`, unless `XATTR_NODEFAULT` is set, the code falls back to default AppleDouble support. Under `DUAL_EAS`, selected `EJUSTRETURN` paths coordinate between native and AppleDouble copies so `XATTR_CREATE`/`XATTR_REPLACE` semantics remain consistent across both backing stores. Successful set/remove operations notify MACF and update multilabel state when needed.

Named streams prefer native filesystem support when `MNTK_NAMED_STREAMS` is set; otherwise only `com.apple.ResourceFork` is implemented by shadow files under `/private/var/run`. Shadow names include kernel-address-permuted vnode identity pieces and `v_id`; shadow directories include `shadow_sequence`. Created stream vnodes are tagged with `VISNAMEDSTREAM`, optionally `VISSHADOW`, linked back to the data vnode as a named-stream parent, and inherit the dyld shared cache flag when relevant.

`getshadowfile()` creates or locates the per-vnode shadow file, copies metadata from the original file when creating it, checks for existing resource fork xattr data, and handles races with existing files or shadow directory removal. `default_getnamedstream()` makes the creator populate the shadow file from the AppleDouble/resource-fork xattr while other callers wait for initialization on the vnode parent channel. `vnode_flushnamedstream()` copies shadow-file data back into the resource fork on close and removes the old resource-fork xattr first because there is no truncate-xattr operation.

`get_shadow_dir()` looks up `/private/var/run`, validates an existing shadow directory, removes invalid entries, and creates a hidden root-owned directory if needed. Validation requires a directory, root ownership, no writable group/other bits, same filesystem as `/private/var/run`, no directory hard links, and no ACLs.

When `CONFIG_APPLEDOUBLE` is enabled, fallback xattr operations get a send right to `doubleagentd`, open or create the AppleDouble `._` sidecar, convert a fileglob to a fileport, drop the vnode iocount before the userspace upcall, call DoubleAgent MIG routines to locate/list/allocate/remove attribute storage, reacquire an iocount, and perform VNOP reads/writes at the offsets DoubleAgent returns.

`open_xattrfile()` finds the sidecar name (`._.` for root directories, otherwise `._<basename>`), blocks sidecar files from having sidecar attributes themselves, uses `DONOTAUTH` because authorization was already performed on the primary vnode, optionally creates the sidecar with inherited ownership/mode, checks owner match, opens and references it, wraps it in a fileglob, and applies advisory locks. `remove_xattrfile()` resolves the sidecar path and removes only if lookup returns the same vnode, avoiding deletion of a raced replacement.

## State and Invariants

- Xattr names must be nonempty valid UTF-8. `xattr_protected()` identifies `com.apple.system.*` attributes as protected by name prefix.
- `XATTR_NOSECURITY` marks trusted kernel paths that bypass user MAC/kauth checks.
- Non-resource-fork xattrs must use zero `uio` offset; resource forks can be read/written with offsets.
- Shadow stream files must be accessed with kernel context to avoid chroot-dependent views of `/private/var/run`.
- Shadow initialization uses `VISNAMEDSTREAM` and `VISSHADOW` flags as readiness/failure signals; waiters sleep on `svp->v_parent`.
- AppleDouble data structures are big-endian/Motorola-aligned and include fixed Finder Info and resource-fork entries plus an attribute header area.
- DoubleAgent fileports are move-send in MIG calls, so the kernel does not retain the send right after the call.
- AppleDouble sidecars are locked shared for reads/lists and exclusive for set/remove layout changes.

## Dependencies

This file depends on XNU VFS/vnode internals, xattr constants, UTF-8 validation, MACF, kauth, namei, vnode identity helpers, VNOP xattr/named-stream operations, AppleDouble constants, fileglob/fileport machinery, Mach host special ports, `doubleagentd` MIG interfaces, and kernel allocation/uio APIs.

It is closely coupled to `vfs_vnops.c` for named stream close/flush behavior and to VFS authorization in `vfs_subr.c`.

## Risks and Edge Cases

- Native and default xattr stores can both exist under `DUAL_EAS`; create/replace/remove semantics depend on carefully probing both stores.
- Shadow streams deliberately create hidden kernel-managed files in `/private/var/run`; directory validation is security-critical.
- Shadow initialization races are subtle: failed creators must mark/wake waiters so another thread can retry.
- Resource fork flushing removes and rewrites the xattr because there is no truncate primitive, so partial-copy failures can affect resource fork persistence.
- The AppleDouble fallback drops vnode iocounts before upcalling to `doubleagentd`; all paths must reacquire and handle vnode identity loss.
- `open_xattrfile()` uses `DONOTAUTH` and relies on prior authorization on the primary vnode, so callers must not expose it as a standalone sidecar access primitive.
- Sidecar removal uses path reconstruction and same-vnode verification to avoid deleting a raced replacement, but failure leaves sidecar cleanup best-effort.
- With `CONFIG_APPLEDOUBLE` disabled, default xattr routines return `ENOTSUP`, changing behavior for filesystems without native xattr support.

## Research Notes

The entire 2,527-line file was read. No per-file output was generated separately in this pass.
