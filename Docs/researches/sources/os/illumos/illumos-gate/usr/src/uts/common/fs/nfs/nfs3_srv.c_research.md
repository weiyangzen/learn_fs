# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs3_srv.c

Implements the illumos in-kernel NFSv3 server procedure handlers, reply cleanup hooks, filehandle extraction hooks, NFSv3 attribute conversion helpers, RDMA read setup, and per-zone server verifier lifecycle.

Key elements:
- Server state: per-zone `nfs3_srv_t` stores the NFSv3 write verifier returned by WRITE/COMMIT. `rfs3_srv_zone_init()` derives it from hostid plus current time, falling back to high-resolution time when hostid is zero.
- Common operation pattern: convert NFSv3 filehandles with `nfs3_fhtovp()`, run DTrace start/done probes, apply export read-only checks with `rdonly()`, apply Trusted Extensions label checks when enabled, use VOP/VFS operations, map errors with `puterrno3()`, convert `T_WOULDBLOCK`/delegation conflicts to `NFS3ERR_JUKEBOX`, and fill post-op or WCC attributes.
- Metadata procedures:
  - `rfs3_getattr()` gets delegated-aware attributes via `rfs4_delegated_getattr()` and reports NFS referral reparse points as symlinks.
  - `rfs3_setattr()` converts `sattr3` to `vattr`, validates guarded ctime, handles size changes with NBMAND conflict checks and `VOP_SPACE()` for owner truncation, applies `VOP_SETATTR()`, fsyncs metadata, and returns WCC data.
  - `rfs3_access()` maps NFSv3 access bits to VOP access checks, accounts for read-only exports, mandatory locks, and label dominance/equality.
- Lookup/readlink:
  - `rfs3_lookup()` supports normal lookup, public filehandle multi-component WebNFS lookup, `..` handling at export roots, nohide climbing, mounted-on traversal, inbound name conversion, security flavor hints, and weak-auth WebNFS status.
  - `rfs3_readlink()` reads symlinks or synthesizes legacy symlink targets for NFS referral reparse points via `build_symlink()`, then performs outbound name conversion.
- I/O:
  - `rfs3_read()` supports RDMA write chunks, STREAMS mblk replies, and TCP loaned zero-copy buffers. It clamps count to transport size, handles EOF and zero-length fast paths, checks NBMAND/read access/mandatory lock state, and prepares RDMA read reply metadata.
  - `rfs3_write()` accepts data from mblks, RDMA read chunks, or inline buffers, enforces count/data length consistency, read-only/type/access/mandatory-lock checks, clamps by file-size limit, chooses stable write flags, temporarily switches `curthread->t_cred` for quota faults, writes through `VOP_WRITE()`, returns WCC and write verifier.
  - `rfs3_commit()` validates regular writable file access and calls `VOP_FSYNC(FSYNC)`, returning WCC plus the write verifier.
- Namespace creation:
  - `rfs3_create()` implements UNCHECKED, GUARDED, and EXCLUSIVE creates. It handles exclusive verifier-as-mtime, required mode validation, nosuid masking, duplicate exclusive create detection, v4 delegation recall conflicts, NBMAND truncation conflicts, fallback size repair, filehandle creation, and fsync of object and parent.
  - `rfs3_mkdir()`, `rfs3_symlink()`, and `rfs3_mknod()` convert attributes/names, enforce labels/read-only/mode requirements, call the relevant VOP, create optional filehandles, collect attributes, and fsync changed metadata.
  - `rfs3_mknod()` maps NFSv3 device/socket/FIFO types to illumos vnode types and requires `secpolicy_sys_devices()` for block/char device creation.
- Namespace mutation:
  - `rfs3_remove()` looks up the target, checks v4 delegation and NBMAND share conflicts, calls `VOP_REMOVE()`, fsyncs the directory, and returns WCC.
  - `rfs3_rmdir()` calls `VOP_RMDIR()` with zone root context and maps `EEXIST` to `ENOTEMPTY` for NFS wire semantics.
  - `rfs3_rename()` verifies source and target exports match, converts names, checks label/read-only constraints, recalls delegations on source/target, checks NBMAND conflicts, calls `VOP_RENAME()`, updates vnode path cache with `vn_renamepath()`, fsyncs both directories, and returns dual WCC.
  - `rfs3_link()` verifies same export, checks label/read-only/name constraints, calls `VOP_LINK()`, fsyncs file and directory, and returns file attrs plus link-directory WCC.
- Directory procedures:
  - `rfs3_readdir()` reads raw `dirent64` entries, enforces response minimum sizing, converts directory entry names via `nfscmd_convdirent()`, and returns an allocated entry buffer freed by `rfs3_readdir_free()`.
  - `rfs3_readdirplus()` reads directory entries, estimates XDR response size including per-entry attrs/filehandles, looks up each returned child, fills post-op attrs and filehandles unless mounted-on, treats referral reparse points as symlinks, converts names via `nfscmd_convdirplus()`, and frees buffers through `rfs3_readdirplus_free()`.
- Filesystem info:
  - `rfs3_fsstat()` maps `VFS_STATVFS()` data to NFSv3 byte/file counters and preserves unknown `-1` block counts.
  - `rfs3_fsinfo()` reports transport transfer sizes, default multiples, directory preference, max file size from `_PC_FILESIZEBITS`, timestamp granularity, and supported properties.
  - `rfs3_pathconf()` reports link/name/chown/truncation pathconf fields and fixed case-sensitive/case-preserving behavior.
- Conversion helpers:
  - `sattr3_to_vattr()` converts optional mode/uid/gid/size/atime/mtime fields, including server-time handling and time overflow checks.
  - `vattr_to_fattr3()`, `vattr_to_wcc_attr()`, `vattr_to_pre_op_attr()`, `vattr_to_post_op_attr()`, and `vattr_to_wcc_data()` convert vnode attributes into NFSv3 fattr/post-op/WCC forms with overflow suppression.
  - `rdma_setup_read_data3()` sizes RDMA read chunks and attaches write chunk metadata to READ replies.
- Per-procedure `*_getfh()` helpers return the request filehandle pointer for dispatch/cache logic. READLINK, READDIR, and READDIRPLUS have explicit result free hooks for allocated response buffers.

Dependencies:
- illumos vnode/VFS APIs: `VOP_GETATTR`, `VOP_SETATTR`, `VOP_SPACE`, `VOP_LOOKUP`, `VOP_CREATE`, `VOP_MKDIR`, `VOP_SYMLINK`, `VOP_REMOVE`, `VOP_RMDIR`, `VOP_RENAME`, `VOP_LINK`, `VOP_READ`, `VOP_WRITE`, `VOP_READDIR`, `VOP_READLINK`, `VOP_FSYNC`, `VOP_ACCESS`, `VOP_RWLOCK`, `VOP_RWUNLOCK`, `VOP_PATHCONF`, `VFS_STATVFS`.
- NFS export/security helpers: `nfs3_fhtovp`, `makefh3`, `makefh3_ol`, `checkexport`, `chk_clnt_sec`, `rdonly`, `rfs_cross_mnt`, `rfs_climb_crossmnt`, `rfs_publicfh_mclookup`, `nfscmd_convname`, `nfscmd_convdirent`, `nfscmd_convdirplus`.
- NFSv4 cross-version support: `rfs4_delegated_getattr()`, `rfs4_check_delegated()`, `vn_is_nfs_reparse()`, `build_symlink()`, and delegation policy checks.
- NBMAND support: `nbl_need_check()`, `nbl_start_crit()`, `nbl_conflict()`, `nbl_end_crit()`.
- RPC/RDMA/STREAMS support: `svc_getrpccaller()`, `rfs3_tsize()`, `rdma_get_wchunk()`, `rdma_setup_read_chunks()`, `rfs_read_alloc()`, `mblk_to_iov()`, `uio_to_mblk()`, `rfs_setup_xuio()`, `VOP_REQZCBUF()`.
- Trusted Extensions label APIs: request labels, `do_rfs_label_check()`, admin-low handling, trusted host lookup for public WebNFS.
- Kernel memory and diagnostics: `kmem_alloc/free`, DTrace probes, kstats referral counter, zone globals.

Research notes:
- NFSv3 server behavior is intentionally coupled to NFSv4 delegation state: v3 writes, truncates, removes, renames, and creates can return JUKEBOX while v4 delegations are recalled.
- Weak cache consistency is pervasive; operations collect before/after attributes where possible, but many paths deliberately return absent attributes if conversion or post-op getattr fails.
- Read and readdir reply ownership is split between XDR response structures and free callbacks; modifying these paths requires preserving exact allocation/free sizes.
- `rfs3_readdirplus()` sets `nvap->va_type = VLNK` for referral entries after `rfs4_delegated_getattr()`; this assumes `nvap` is non-NULL when referral detection succeeds.
