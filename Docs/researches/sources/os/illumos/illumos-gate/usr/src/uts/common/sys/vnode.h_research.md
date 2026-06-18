# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vnode.h

## Role

`vnode.h` is the primary illumos vnode contract. It defines vnode types, vnode structure layout, vnode flags, vnode attributes, extensible attributes, security attributes, caller context, vnode operation signatures, VOP dispatch macros, vnode lifecycle helpers, vnode path-cache behavior, event notifications, and VM/page integration hooks.

## Core Data Structures

`vopstats_t` records per-operation kstats for VOP calls and byte counts for read/write/readdir.

`vnode_t` contains public fields such as lock, flags, refcount, filesystem-private data, containing VFS, stream pointer, type, and device number. It also contains private fields for mounted VFS, operation vector, page list, locks, FEM hooks, path cache, mmap/open counts, MPSS data, file-operation watches, vnode-specific data, xattr directory vnode, and DNLC refcount.

The header explicitly warns that vnodes must be allocated through `vn_alloc()` and must not be embedded in filesystem-private nodes.

## Path Cache Model

The file documents `v_path` and `v_path_stamp` in detail. Filesystem lookup/create/mkdir code updates cached paths when parent context is known. Directory renames update the renamed vnode directly but leave descendants potentially stale; later lookups refresh stale children by comparing path stamps.

## Attributes

`vattr_t` defines classic vnode attributes: type, mode, owner, group, fsid, node ID, link count, size, timestamps, rdev, block size, block count, and sequence number.

`xoptattr_t` and `xvattr_t` define extensible attributes such as create time, archive/system/readonly/hidden bits, nounlink, immutable, append-only, nodump, opaque, antivirus quarantine/modified/scanfingerprint, reparse, generation, offline, sparse, project inheritance, and project ID.

Macros define classic `AT_*` masks, optional `XAT_*` masks, and helpers to set/check requested and returned xvattr bits.

## Vnode Operations

`VNODE_OPS` defines the complete vnode operation vector, including:
- open/close/read/write/ioctl/setfl,
- getattr/setattr/access,
- lookup/create/remove/link/rename/mkdir/rmdir/readdir/symlink/readlink,
- fsync/inactive/fid,
- rwlock/rwunlock/seek/cmp/frlock/space/realvp,
- getpage/putpage/map/addmap/delmap,
- poll/dump/pathconf/pageio/dumpctl/dispose,
- get/set security attributes,
- share locks,
- vnode events,
- zero-copy buffer request/return.

The file declares `fop_*` generic dispatch wrappers and defines `VOP_*` macros that route through those wrappers.

## Security, Events, and Context

`vsecattr_t` carries ACL and ACE data for `VOP_GETSECATTR` and `VOP_SETSECATTR`.

`caller_context_t` carries caller PID, system ID, caller ID, and flags such as `CC_DONTBLOCK` and `CC_WOULDBLOCK`.

`vnevent_t` enumerates rename, remove, create, link, mount-over, truncate, and pre-rename notifications. Helper functions emit these events.

## Lifecycle and VM Integration

Kernel helpers cover vnode allocation/reinit/recycle/free, read-only/open/mapped checks, open-count transitions, flock and mandatory-lock checks, cached-data checks, operation-vector accessors, mountpoint locks, spec vnode creation, path manipulation, vnode-specific data, xattr/reparse initialization, caller ID allocation, MPSS/pageio decisions, and vnode reference macros.

`VN_HOLD` and `VN_RELE` wrappers centralize reference-count changes and emit DTrace probes. `VN_DISPOSE()` routes page disposal through `VOP_DISPOSE()` when the page belongs to a real vnode and otherwise frees/destroys kernel-address-space pages.

## Research Notes

This header is one of the most sensitive ABI/internal-contract files in the VFS stack. Filesystems should treat most vnode fields as private and use `vn_*`, `VOP_*`, and operation-registration helpers. Attribute bitmap macros contain assertions using bitwise OR checks; users must initialize `xvattr_t` with `xva_init()`.
