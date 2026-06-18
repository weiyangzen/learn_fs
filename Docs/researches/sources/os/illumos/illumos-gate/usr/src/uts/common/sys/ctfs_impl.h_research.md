# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctfs_impl.h

Private implementation header for the contract filesystem. It defines CTFS synthetic inode encodings, per-vnode private data structures, endpoint listener state, VFS state, vnode creation helpers, common access/open/close helpers, and vnodeops templates.

Key elements:
- Encodes root inode as zero, contract-specific files with the high bit set plus file number and contract id, and type-specific files with type/file fields.
- Provides macros for contract directory, `all` symlink, contract special files, type directories, and type special files.
- Defines `CTFS_NAME_MAX` and endpoint flags for setup and nonblocking mode.
- `ctfs_endpoint_t` combines a mutex, contract listener, and endpoint flags.
- Root, `all`, type-directory, and latest nodes are represented using `gfs_dir_t`.
- `ctfs_symnode_t` stores a GFS file, target contract, symlink target string, and string length.
- `ctfs_cdirnode_t` stores contract-directory contents, target contract, and contract vnode-list linkage.
- Template, ctl/status, events, and bundle/pbundle node structs store the GFS file plus the relevant contract/template/event queue/listener state.
- `ctfs_vfs_t` stores the root vnode for the mounted CTFS instance.
- Declares vnode factory functions for type dirs, templates, latest, bundles, ctl/status, events, `all`, contract dirs, and symlinks.
- Declares shared getattr, close, access, and open helpers.
- Exposes vnodeops vectors for each CTFS virtual file type.

Dependencies:
- Depends on the contract subsystem and generic filesystem (`gfs`) support.
- Uses vnode/vattr/cred/caller context types from the kernel VFS layer through included contract/GFS headers.

Research notes:
- The inode encoding is part of CTFS's stable synthetic namespace; changing it would affect vnode identity and filesystem behavior.
- Endpoint nodes embed listener state directly, so open/read/ioctl paths must coordinate endpoint setup and blocking flags under `ctfs_endpt_lock`.
