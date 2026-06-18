# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_srv.c

## Purpose
Implements the server-side NFSv2 RPC procedures for illumos, translating wire-level NFSv2 operations into vnode/VFS operations and returning protocol attributes, filehandles, directory data, and status codes.

## Key Elements
Provides handlers for NFSv2 `getattr`, `setattr`, `lookup`, `readlink`, `read`, `write`, `create`, `remove`, `rename`, `link`, `symlink`, `mkdir`, `rmdir`, `readdir`, and `statfs`, plus matching `*_getfh` helpers and response-free routines. It converts filehandles with `nfs_fhtovp`, enforces read-only exports with `rdonly`, maps VFS errors through `puterrno`, and forces stable-storage semantics with `VOP_FSYNC`, `VOP_PUTPAGE`, or synchronous writes where required by the protocol.

The file handles compatibility details specific to NFSv2: 32-bit attribute overflow detection, legacy device-number compression/expansion, FIFO/special-file over-the-wire encodings, `sattr_to_vattr`, `vattr_to_nattr`, and the overloaded mtime nanosecond sentinel used to request server time. `acl_perm` approximates ACL permissions in returned mode bits, using restrictive or permissive behavior depending on export flags.

Path handling includes public filehandle/WebNFS lookup, multicomponent public lookup, referral symlink fabrication, charset/name conversion through `nfscmd_convname` and directory conversion helpers, `EX_NOHIDE` mount crossing with `rfs_cross_mnt`, and climbing above a nohide exported root with `rfs_climb_crossmnt`. Several write and namespace operations check NFSv4 delegations and set `T_WOULDBLOCK` to drop replies so clients retry after recall.

Write support has both `rfs_write_sync` and clustered `rfs_write`. The clustered path builds per-file async write lists protected by a per-zone `nfs_srv_t`, sorts requests by offset, coalesces contiguous data into larger `VOP_WRITE` calls, broadcasts completions to waiting service threads, and flushes changed ranges to stable storage.

## Dependencies
Depends on illumos vnode/VFS interfaces, credentials, zones, kstats, RPC/SVC request state, stream `mblk_t` buffers, VM/page interfaces, NFS export data, NFS ACL/security support, non-blocking mandatory lock helpers, RDMA chunk helpers, WebNFS/public filehandle routines, and NFSv4 delegation/referral support.

## Behavior/Risks
The handlers contain many protocol compatibility branches, so changes can break old NFSv2 clients even if they look redundant. Error paths must preserve vnode/export reference balancing and must distinguish normal errors from delegation conflicts that require `T_WOULDBLOCK`. The clustered write path uses stack-backed queue nodes while peer service threads wait on condition variables, making lifetime, locking, and status initialization (`RFSWRITE_INITVAL`) critical. Attribute conversion intentionally rejects values not representable in NFSv2, which can surface as `EFBIG`, `EOVERFLOW`, or `NFSERR_INVAL` for modern large files or timestamps.
