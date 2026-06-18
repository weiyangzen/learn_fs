# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_xdr.c

## Purpose
Provides XDR encode/decode/free routines for NFSv2 protocol structures used by both client and server paths, with optimized inline encoders/decoders and special support for mblk and RDMA transports.

## Main Entry Points
- File handles and attributes: `xdr_fhandle()`, `xdr_fastfhandle()`, `xdr_fattr()`, `xdr_fastfattr()`, `xdr_nfs2_timeval()`.
- Read/write: `xdr_writeargs()`, `xdr_readargs()`, `xdr_rrok()`, `xdr_rdresult()`.
- Attribute/status results: `xdr_sattr()`, `xdr_attrstat()`, `xdr_fastattrstat()`, `xdr_saargs()`.
- Symlink/readlink: `xdr_readlink()`, `xdr_srok()`, `xdr_rdlnres()`, `xdr_slargs()`.
- Readdir: `xdr_rddirargs()`, `xdr_putrddirres()`, `xdr_getrddirres()`.
- Directory ops: `xdr_diropargs()`, `xdr_drok()`, `xdr_fastdrok()`, `xdr_diropres()`, `xdr_fastdiropres()`, `xdr_creatargs()`, `xdr_linkargs()`, `xdr_rnmargs()`.
- Statfs and fast helpers: `xdr_fsok()`, `xdr_fastfsok()`, `xdr_statfs()`, `xdr_faststatfs()`, `xdr_fastenum()`, `xdr_fastshorten()`.

## Internal Mechanics
Most routines first try `XDR_INLINE()` to encode/decode fixed-size fields directly as 32-bit XDR words. If inline storage is unavailable, they fall back to generic `xdr_*` helpers. Little-endian fast paths mutate structures into network order for pre-sized replies, while big-endian fast paths can often leave already laid-out data in place.

`xdr_writeargs()` supports normal byte arrays, mblk-backed data (`xdrmblk_getmblk()`), and RDMA read-from-client paths. Its `XDR_FREE` branch releases RDMA clists and allocated write buffers.

`xdr_readargs()` records expected RDMA write chunks during sizing/encoding and decodes RDMA write-list connection state. `xdr_rrok()` handles read replies over normal XDR, mblk XDR, and RDMA write chunks, including count-only replies when data is transferred by RDMA.

Readdir encoding converts kernel `dirent64` records into NFSv2 wire entries with 32-bit inode/cookie validation. Decode reconstructs `dirent64` records into the caller buffer and reports partial-buffer overflow by returning the bytes filled and next cookie.

Directory operation argument decoding allocates names when needed, enforces `NFS_MAXNAMLEN`, null-terminates names, and rejects embedded NULs by comparing `strlen()` with the XDR length. Free paths release only names marked with local free flags.

## Dependencies
Uses illumos RPC/XDR APIs, stream mblk XDR operations, RDMA XDR operations, NFSv2 protocol structs/constants, kernel memory allocation, dirent layout macros, and endian conversion helpers.

## Risks and Notes
- Many routines assume exact NFSv2 fixed layout and rely on 32-bit truncation checks for inode/cookie fields.
- RDMA paths have distinct encode/decode/free ownership rules for clists and transferred data.
- Fast little-endian routines convert structures in place, so callers must only use them in contexts expecting that mutation.
- `xdr_fastshorten()` adjusts XDR stream position to strip unused union payload space in fast reply paths.
