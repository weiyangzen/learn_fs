# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs3_xdr.c

## Purpose

`nfs3_xdr.c` contains the illumos NFSv3 XDR encode/decode routines used by both NFS client and server code. It serializes NFSv3 RPC arguments and results, decodes server responses into kernel-native structures, supports inline fast paths, and integrates with RDMA and mblk-backed XDR streams.

The file is protocol plumbing, but it also enforces important safety and interoperability rules: bounded string decoding, filehandle validation, size/time overflow handling, directory response bounds checks, and direct decode into `vattr_t`, `dirent64_t`, or `uio`.

## Main Interfaces

Important public XDR routines include:

- Basic types: `xdr_string3`, `xdr_nfs_fh3`, `xdr_nfs_fh3_server`, `xdr_diropargs3`, `xdr_post_op_attr`, `xdr_post_op_fh3`
- Attribute operations: `xdr_GETATTR3res`, `xdr_GETATTR3vres`, `xdr_SETATTR3args`, `xdr_SETATTR3res`
- Lookup/access/readlink: `xdr_LOOKUP3res`, `xdr_LOOKUP3vres`, `xdr_ACCESS3args`, `xdr_ACCESS3res`, `xdr_READLINK3args`, `xdr_READLINK3res`
- Data I/O: `xdr_READ3args`, `xdr_READ3res`, `xdr_READ3vres`, `xdr_READ3uiores`, `xdr_WRITE3args`, `xdr_WRITE3res`
- Namespace operations: `xdr_CREATE3args`, `xdr_CREATE3res`, `xdr_MKDIR3args`, `xdr_MKDIR3res`, `xdr_SYMLINK3args`, `xdr_SYMLINK3res`, `xdr_MKNOD3args`, `xdr_MKNOD3res`, `xdr_REMOVE3res`, `xdr_RMDIR3res`, `xdr_RENAME3args`, `xdr_RENAME3res`, `xdr_LINK3args`, `xdr_LINK3res`
- Directory operations: `xdr_READDIR3args`, `xdr_READDIR3res`, `xdr_READDIR3vres`, `xdr_READDIRPLUS3args`, `xdr_READDIRPLUS3res`, `xdr_READDIRPLUS3vres`
- Filesystem metadata: `xdr_FSSTAT3res`, `xdr_FSINFO3res`, `xdr_PATHCONF3res`
- Commit: `xdr_COMMIT3args`, `xdr_COMMIT3res`

Several helpers are private: `xdr_decode_nfs_fh3`, `xdr_encode_nfs_fh3`, `xdr_fattr3`, `xdr_fattr3_to_vattr`, `xdr_post_op_vattr`, `xdr_wcc_data`, `xdr_sattr3`, `xdr_putdirlist`, and `xdr_putdirpluslist`.

## Filehandle Encoding

The file has two NFSv3 filehandle paths:

- `xdr_nfs_fh3()` is the generic counted opaque filehandle routine.
- `xdr_nfs_fh3_server()` uses illumos-specific internal filehandle knowledge for server-side encode/decode unless `FH_WEBNFS` requires generic encoding.

`xdr_inline_decode_nfs_fh3()` validates total size and component sizes before reconstructing the internal `nfs_fh3`. It handles native-order internal fields, unaligned length fields, historical `NFS_FHMAXDATA` padding behavior, and final XDR alignment. Malformed filehandles are decoded far enough to preserve stream position but leave a zero length so the NFS layer can reject them.

`xdr_inline_encode_nfs_fh3()` computes on-the-wire length, rounds to an XDR word boundary, zeroes padding, and writes the internal handle layout into the XDR stream.

## String And Attribute Handling

`xdr_string3()` treats protocol strings as counted strings but returns C strings to callers. On decode it rejects embedded NULs by comparing `strlen()` to the counted length. Names that exceed the local max are skipped with `XDR_SKIPBYTES` and represented by the sentinel `nfs3nametoolong`.

`xdr_fattr3()` is the raw NFSv3 attribute serializer. `xdr_fattr3_to_vattr()` is the client-oriented fast decoder that writes directly into `vattr_t`. It converts NFS file types to vnode types, maps nobody uid/gid values, validates file sizes with `NFS3_SIZE_OK`, handles optional pre-epoch time behavior, checks time overflow, computes `va_nblocks`, and fills device numbers for character/block special files.

`xdr_post_op_vattr()` decodes optional post-op attributes into `vattr_t` and drops invalid attributes by clearing the `attributes` boolean. `xdr_post_op_attr()` is the raw `fattr3` variant. `xdr_wcc_data()` handles weak cache consistency pre/post attributes and validates pre-op times on 32-bit builds.

## RPC Result Patterns

Most operation result encoders/decoders follow the NFSv3 discriminated-union pattern:

1. Decode or encode `status`.
2. If status is not `NFS3_OK`, serialize failure attributes or WCC data.
3. If status is OK, serialize operation-specific payload and post-op/WCC data.

This appears in SETATTR, CREATE, MKDIR, SYMLINK, MKNOD, REMOVE, RMDIR, RENAME, LINK, WRITE, COMMIT, FSSTAT, FSINFO, and PATHCONF.

The client vnode code in `nfs3_vnops.c` relies on these routines to leave caches in a useful state even after errors, because failure arms frequently carry post-op attrs or WCC data.

## READ/WRITE And RDMA Support

`xdr_READ3args()` supports ordinary XDR plus RDMA write chunks. It can register a reply write chunk backed by either a `uio` or an address buffer. On RDMA decode it records the write list and connection.

`xdr_READ3res()` supports server-side encoding with inline data, mblk data, or RDMA_WRITE transfer through `xdrrdma_send_read_data()`.

`xdr_READ3vres()` is the normal client decode path into an address buffer and validates RDMA write-list byte counts. `xdr_READ3uiores()` is direct-I/O oriented: it skips attributes, decodes into a `uio`, supports `xdrmblk_ops`, RDMA write-list completion, inline XDR buffers, and fallback temporary allocation.

`xdr_WRITE3args()` supports ordinary bytes, mblk decode, and RDMA read-from-client via `xdrrdma_getrdmablk()` and `xdrrdma_read_from_client()`. Its FREE path releases RDMA clists. `xdr_WRITE3res()` decodes WCC data, count, stable commit mode, and write verifier, treating the verifier as an XDR hyper for efficiency.

## Directory Handling

`xdr_READDIR3res()` and `xdr_putdirlist()` encode server directory listings while respecting the requested byte count. Entry sizing includes list booleans, fileid, name length, padded name bytes, cookie, final false marker, and EOF marker.

`xdr_READDIR3vres()` decodes client directory responses directly into a caller-provided `dirent64_t` buffer. It checks each record length, stops cleanly if the output buffer would overflow, updates `loff` from the decoded cookie, and returns the number of bytes filled.

`xdr_READDIRPLUS3vres()` extends this by also decoding each entry's post-op attributes and optional filehandle. When both are valid and the name is not `"."`, it creates or finds an NFS node with `makenfs3node_va()` and updates the DNLC. This makes XDR decode an active participant in client name-cache population.

## Safety Properties

Notable defensive behavior:

- String lengths are bounded and oversized strings are skipped rather than over-read.
- Optional booleans are validated as true/false in multiple places.
- Filehandle size and internal component sizes are validated.
- Attribute sizes and times can invalidate attributes without breaking full response decode.
- Directory decode stops before overflowing caller buffers.
- READ RDMA paths verify transferred lengths match protocol counts.
- WRITE RDMA clists are released in the FREE path.
- Server-side READDIR encoding respects response count limits.

## Dependencies

This file depends on:

- RPC/XDR core APIs and inline XDR macros.
- RDMA XDR support: `xdrrdma_ops`, `xdrrdmablk_ops`, RDMA chunk controls, clists.
- mblk XDR support: `xdrmblk_ops`.
- NFS vnode/rnode helpers, especially `makenfs3node_va()` and DNLC update for READDIRPLUS.
- NFS constants and conversion helpers such as `nf3_to_vt`, `NFS3_SIZE_OK`, `NFS3_TIME_OVERFLOW`, `nfs3tsize()`, and `nfs_allow_preepoch_time`.

## Research Notes

This file is a critical trust boundary. It converts untrusted network byte streams into kernel structures. The code is optimized for the common inline XDR path but contains fallback paths for stream types and allocation failures. The most important audit areas are filehandle validation, directory buffer accounting, RDMA count validation, `xdr_string3()` sentinel handling, and any path where invalid attributes must be ignored without desynchronizing the XDR stream.
