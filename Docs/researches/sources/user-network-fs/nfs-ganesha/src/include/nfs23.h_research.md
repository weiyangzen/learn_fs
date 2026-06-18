# sources/user-network-fs/nfs-ganesha/src/include/nfs23.h

## Purpose

`nfs23.h` is the mixed rpcgen/hand-maintained wire contract for NFSv2 compatibility and NFSv3 service support. It defines status codes, scalar aliases, file handle layouts, attribute/result structures, every NFSv3 procedure argument/result type, procedure numbers, and XDR routines.

## Important APIs, Types, and Functions

Important constants include NFSv2 limits, `NFS3_FHSIZE`, verifier sizes, `NFS_PROGRAM`, `NFS_V2`, `NFS_V3`, and `NFSPROC3_*`. Core wire types include `nfsstat3`, `ftype3`, `nfs_fh3`, `nfstime3`, `fattr3` aliasing `struct fsal_attrlist`, `post_op_attr`, `pre_op_attr`, `wcc_data`, `sattr3`, `diropargs3`, read/write data structures, directory entry lists with `xdr_uio`, and FSINFO/PATHCONF/COMMIT results. XDR declarations cover every scalar, compound, operation argument/result, and optimized readdir entry encoder/release helper.

## Control Flow

RPC dispatch tables decode requests into these structures, call NFSv3 handlers, then encode status-specific result unions. Many result unions carry weak-cache-consistency data on both success and failure. READ/WRITE carry `io_data`; READDIR/READDIRPLUS can stream via `xdr_uio`.

## State and Persistence Behavior

The header has no runtime state but defines how persistent filesystem attributes, file IDs, handles, cookies, and write verifiers are exposed on the wire. Because `fattr3` aliases FSAL attributes, FSAL attribute lifetime and initialization directly affect encoded protocol data.

## Dependencies and Integration Points

It depends on `gsh_rpc.h`, `extended_types.h`, `mount.h`, and `fsal_types.h`. It is central to `nfs_proto_data.h`, protocol function descriptors, file-handle conversion, NFSACL, MOUNT, metrics, and NFSv3 XDR implementation.

## Risks and Test Signals

Risks include layout coupling with `mount.h` `fhandle3`, manual divergence from rpcgen, flexible-array C/C++ differences, union free mistakes, wrong WCC data on failures, and readdir UIO lifetime bugs. Tests should XDR round-trip every op, fuzz lengths and handles, verify procedure table bounds, exercise READ/WRITE payloads, READDIRPLUS streaming/release, 32/64-bit scalar encoding, and NFSv3 conformance cases for status-specific unions.
