# File Research: sources/os/bsd/netbsd-src/sys/sys/vnode.h

Read completely: 683 lines.

Central public kernel vnode contract for NetBSD VFS. It defines vnode types/tags, the public `struct vnode`, vnode attribute and permission models, VOP dispatch metadata, vnode operation vector descriptors, and exported vnode/VFS helper APIs.

Core vnode model:
- `enum vtype` covers regular files, directories, devices, symlinks, sockets, FIFOs, bad vnodes, and no-type.
- `enum vtagtype` identifies filesystem family for external tools, including UFS, NFS, LFS, tmpfs, puffs, zfs, nilfs, v7fs, chfs, autofs, and others.
- `struct vnode` contains the UVM object, file size/write size, synchronization state, use/write/hold counts, clean/dirty buffer lists, mount/op-vector references, type/tag/data, vnode kqueue state, and type-specific union data for mountpoints, sockets, devices, FIFOs, or read-ahead context.
- Field comments document lock ownership: vnode interlock, buffer cache lock, UVM object lock, vnode lock, exec lock, filesystem locking, and mount/vnode-list locks.

Flags and attributes:
- `VV_*` flags cover root/system/tty/mapped/MPSAFE state.
- `VI_*` flags cover text/executable/write mappings, resident pages, syncer list membership, and dead-check needs.
- `VU_DIROP` is an underlying-filesystem flag used by LFS directory operations.
- `struct vattr` holds type, mode, ownership, fsid, fileid, size, block size, timestamps, generation, flags, rdev, disk bytes, file revision, and operation flags.
- Kernel `ioflag` bits express sync/direct/journal/append/node-locked/ext-attr behavior and access pattern advice.
- VFS access bits include traditional read/write/exec plus NFSv4-style ACL permissions and derived permission groups.

Dispatch and helper API:
- `struct vnodeop_desc`, `vnodeopv_entry_desc`, and `vnodeopv_desc` describe generated VOP operation offsets, names, vnode argument offsets, returned vnode pointer offsets, credential/componentname offsets, and willrele/willput flags.
- `VCALL`, `VOCALL`, `VDESC`, and `VOFFSET` are the low-level VOP dispatch macros.
- Includes generated `<sys/vnode_if.h>` in kernel builds.
- Declares public vnode lifecycle/cache/sync helpers such as `vref`, `vrele`, `vput`, `vn_lock`, `vgone`, `vflush`, `vinvalbuf`, `vcache_get`, `vcache_new`, `vcache_rekey_*`, `vn_open`, `vn_rdwr`, `vn_readdir`, `vn_stat`, `vn_extattr_*`, and vnode/device helpers.
- Provides vnode kqueue interest helpers `VN_KEVENT_INTEREST` and `VN_KNOTE`.

Risks and notes:
- Lock annotations are part of the contract; VFS and filesystem code must follow them to avoid vnode/buffer/VM races.
- `v_tag` is explicitly for external programs and should not drive kernel behavior.
- VOP descriptor metadata must match generated wrappers and filesystem operation vectors.
